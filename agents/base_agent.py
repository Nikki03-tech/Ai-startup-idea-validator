import time
from google import genai
from google.genai import types

def generate_content_with_retry(client, model, contents, max_retries=3, delay=10):
    """
    Handles API calls with retries for transient 500 (Server Error) and 429 (Rate Limit) errors.
    """
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model,
                contents=contents
            )
            return response
        except Exception as e:
            err_str = str(e).lower()
            # If server error (500), unexpected EOF, or rate limit (429), retry
            if ("500" in err_str or "eof" in err_str or "429" in err_str) and attempt < max_retries - 1:
                print(f"[Retry Warning] Connection failed ({e}). Retrying in {delay}s (Attempt {attempt + 1}/{max_retries})...")
                time.sleep(delay)
            else:
                raise e