"""Centralized Gemini configuration: automatic API key rotation + model
factory.

Every agent (agents/*.py) and the Orchestrator (app/orchestrator.py)
get their Gemini client/model from this module instead of reading
GEMINI_API_KEY(S) / STARTUP_VALIDATOR_MODEL or constructing
ChatGoogleGenerativeAI / google.genai.Client themselves. This is the
ONLY place in the project that resolves which Gemini API key is
active, detects quota/rate-limit/auth failures, and rotates keys.

Gemini-only by design - this is not a multi-provider abstraction.

Automatic key rotation
-----------------------
Configure a pool of keys (see .env.example):

    GEMINI_API_KEYS=key1,key2,key3

The first key is used normally. If a request fails with a Gemini
quota/rate-limit/authentication error (HTTP 429 / RESOURCE_EXHAUSTED,
401/403, etc.), this module automatically moves to the next configured
key and retries the *same* request - no manual index, no restart. The
new active key is shared process-wide, so every agent still to run in
the current (or a later) validation also skips the exhausted key.
If every configured key fails, a single clear RuntimeError is raised
(never containing any key value).

GEMINI_API_KEY (single key) still works unchanged for anyone not using
rotation. GEMINI_API_KEYS takes precedence over GEMINI_API_KEY when
both are set.

Why recreating the model matters
---------------------------------
ChatGoogleGenerativeAI builds its underlying client once, at
construction time, from whichever key it was given - mutating
`.google_api_key` on an existing instance afterward does NOT change
the client a later call would use. So "switching keys" here always
means running the retry against a genuinely different, separately
constructed ChatGoogleGenerativeAI instance (see
RotatingChatGoogleGenerativeAI below) - never just flipping a
variable on an already-built client.
"""

from __future__ import annotations

import threading
from typing import Any, Awaitable, Callable, Optional, TypeVar

from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import PrivateAttr

from app.config import settings

T = TypeVar("T")


# ---------------------------------------------------------------------
# Key pool: shared, in-memory, process-lifetime rotation state.
# ---------------------------------------------------------------------


def _configured_keys() -> list[str]:
    """Return the configured pool of Gemini API keys, in order.

    GEMINI_API_KEYS (comma-separated) takes precedence over the single
    GEMINI_API_KEY when both are set.
    """

    if settings.GEMINI_API_KEYS:
        keys = [k.strip() for k in settings.GEMINI_API_KEYS.split(",") if k.strip()]
        if keys:
            return keys

    if settings.GEMINI_API_KEY:
        return [settings.GEMINI_API_KEY]

    return []


class _GeminiKeyPool:
    """The configured Gemini API keys plus which one is currently active.

    Purely in-memory and process-lifetime - never persisted, logged, or
    exposed. Advancing is thread-safe so concurrent agents that hit the
    same exhausted key don't skip past more keys than necessary.
    """

    def __init__(self, keys: list[str]):
        self._keys = keys
        self._active_index = 0
        self._lock = threading.Lock()

    def __len__(self) -> int:
        return len(self._keys)

    def current_index(self) -> int:
        with self._lock:
            return self._active_index

    def key_at(self, index: int) -> str:
        return self._keys[index]

    def advance(self, from_index: int) -> Optional[int]:
        """Move past the key at from_index.

        Returns the new active index, or None if from_index was
        already the last configured key (every key has now failed).
        If another caller already advanced past from_index (a
        concurrent failure on the same key), this just returns the
        current index instead of advancing twice.
        """

        with self._lock:
            if self._active_index == from_index:
                if from_index + 1 >= len(self._keys):
                    return None
                self._active_index = from_index + 1
            return self._active_index


_pool: Optional[_GeminiKeyPool] = None
_pool_init_lock = threading.Lock()


def _key_pool() -> _GeminiKeyPool:
    global _pool
    if _pool is None:
        with _pool_init_lock:
            if _pool is None:
                keys = _configured_keys()
                if not keys:
                    raise RuntimeError(
                        "No Gemini API key configured. Set GEMINI_API_KEY "
                        "(or GEMINI_API_KEYS for automatic rotation) in "
                        "your environment or .env file."
                    )
                _pool = _GeminiKeyPool(keys)
    return _pool


def get_gemini_api_key() -> str:
    """Return the currently active Gemini API key (reflects rotation)."""

    pool = _key_pool()
    return pool.key_at(pool.current_index())


# ---------------------------------------------------------------------
# Quota/rate-limit/auth error detection.
#
# Duck-typed on purpose: the google-genai SDK raises
# google.genai.errors.ClientError (with a numeric .code/.status), and
# langchain-google-genai may re-wrap it. Rather than hard-import an
# exact exception class that could change across versions, we check
# structured attributes first and fall back to matching the message.
# ---------------------------------------------------------------------

_ROTATABLE_STATUS_CODES = {401, 403, 429}
_ROTATABLE_STATUS_NAMES = {"RESOURCE_EXHAUSTED", "PERMISSION_DENIED", "UNAUTHENTICATED"}
_ROTATABLE_MESSAGE_MARKERS = (
    "429",
    "401",
    "403",
    "resource_exhausted",
    "rate limit",
    "rate_limit",
    "quota",
    "unauthenticated",
    "permission_denied",
    "api_key_invalid",
    "invalid api key",
)


def _is_rotatable_gemini_error(exc: BaseException) -> bool:
    code = getattr(exc, "code", None)
    if isinstance(code, int) and code in _ROTATABLE_STATUS_CODES:
        return True

    status = getattr(exc, "status", None) or getattr(exc, "reason", None)
    if isinstance(status, str) and status.upper() in _ROTATABLE_STATUS_NAMES:
        return True

    message = str(exc).lower()
    return any(marker in message for marker in _ROTATABLE_MESSAGE_MARKERS)


# ---------------------------------------------------------------------
# Shared rotation loop - used by both the LangChain-based agents (via
# RotatingChatGoogleGenerativeAI below) and app/orchestrator.py's raw
# google-genai SDK call, so the retry/rotation logic itself is never
# duplicated between the two call paths.
# ---------------------------------------------------------------------


def _advance_or_raise(pool: _GeminiKeyPool, index: int, exc: BaseException) -> bool:
    """Return True if the caller should retry with the new active key.

    Raises RuntimeError (never containing a key value) if every
    configured key has now failed.
    """

    if not _is_rotatable_gemini_error(exc):
        return False

    next_index = pool.advance(index)
    if next_index is None:
        raise RuntimeError(
            f"All {len(pool)} configured Gemini API key(s) were rejected "
            "due to quota/rate-limit or authentication errors. Configure "
            "a working GEMINI_API_KEY or GEMINI_API_KEYS and try again."
        ) from exc

    return True


def run_with_gemini_key_rotation(call_with_key: Callable[[str, int], T]) -> T:
    """Call call_with_key(active_key, active_index), rotating and
    retrying on quota/rate-limit/auth errors until it succeeds or every
    configured key has failed.
    """

    pool = _key_pool()
    while True:
        index = pool.current_index()
        key = pool.key_at(index)
        try:
            return call_with_key(key, index)
        except Exception as exc:
            if not _advance_or_raise(pool, index, exc):
                raise


async def arun_with_gemini_key_rotation(
    call_with_key: Callable[[str, int], Awaitable[T]],
) -> T:
    """Async counterpart of run_with_gemini_key_rotation."""

    pool = _key_pool()
    while True:
        index = pool.current_index()
        key = pool.key_at(index)
        try:
            return await call_with_key(key, index)
        except Exception as exc:
            if not _advance_or_raise(pool, index, exc):
                raise


# ---------------------------------------------------------------------
# Rotation-aware chat model.
#
# Subclasses ChatGoogleGenerativeAI (rather than reimplementing a
# provider-agnostic wrapper) so Gemini-specific behavior it already
# implements - bind_tools() tool-schema conversion, with_structured_
# output(), etc. - keeps working unchanged; only the two low-level
# hooks that actually make the network call are overridden.
# ---------------------------------------------------------------------


class RotatingChatGoogleGenerativeAI(ChatGoogleGenerativeAI):
    # Index this instance's own (already-built) client corresponds to.
    _own_index: int = PrivateAttr(default=0)
    # kwargs (model name, temperature, max_retries, ...) needed to
    # build a genuinely separate ChatGoogleGenerativeAI for any other
    # key in the pool - never reused/mutated, always freshly built.
    _delegate_kwargs: dict = PrivateAttr(default_factory=dict)
    _delegates: dict = PrivateAttr(default_factory=dict)

    def _delegate_for(self, index: int) -> ChatGoogleGenerativeAI:
        if index == self._own_index:
            return self
        if index not in self._delegates:
            self._delegates[index] = ChatGoogleGenerativeAI(
                google_api_key=_key_pool().key_at(index),
                **self._delegate_kwargs,
            )
        return self._delegates[index]

    def _generate(self, messages, stop=None, run_manager=None, **kwargs: Any):
        def _call(_key: str, index: int):
            delegate = self._delegate_for(index)
            if delegate is self:
                return ChatGoogleGenerativeAI._generate(
                    self, messages, stop=stop, run_manager=run_manager, **kwargs
                )
            return delegate._generate(messages, stop=stop, run_manager=run_manager, **kwargs)

        return run_with_gemini_key_rotation(_call)

    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs: Any):
        async def _call(_key: str, index: int):
            delegate = self._delegate_for(index)
            if delegate is self:
                return await ChatGoogleGenerativeAI._agenerate(
                    self, messages, stop=stop, run_manager=run_manager, **kwargs
                )
            return await delegate._agenerate(
                messages, stop=stop, run_manager=run_manager, **kwargs
            )

        return await arun_with_gemini_key_rotation(_call)


def get_chat_model(model_name: str | None = None, **kwargs) -> ChatGoogleGenerativeAI:
    """Build a rotation-aware Gemini chat model.

    Parameters
    ----------
    model_name:
        Optional override. Defaults to STARTUP_VALIDATOR_MODEL (via
        Settings), same default every agent already used.
    **kwargs:
        Forwarded to ChatGoogleGenerativeAI - e.g. max_retries=1, which
        every agent already set explicitly to avoid the library's
        default of up to 6 silent retries multiplying quota usage on
        429s. This still applies per key: a key is given at most that
        many attempts before rotation moves to the next one, so
        max_retries doesn't block rotation - it just stops us wasting
        retries hammering a key that's already exhausted.
    """

    resolved_model_name = model_name or settings.STARTUP_VALIDATOR_MODEL
    pool = _key_pool()
    index = pool.current_index()

    model = RotatingChatGoogleGenerativeAI(
        model=resolved_model_name,
        google_api_key=pool.key_at(index),
        **kwargs,
    )
    model._own_index = index
    model._delegate_kwargs = {"model": resolved_model_name, **kwargs}
    return model
