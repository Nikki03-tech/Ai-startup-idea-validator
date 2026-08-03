"""Context Passer

Handles context transfer, state updates, and confidence scoring between pipeline agents.
"""
"""Context Passer

Handles context transfer, state updates, and confidence scoring between pipeline agents.
"""
from state.memory import SharedMemory


def update_memory(memory: SharedMemory, key: str, value):
    """
    Update a field in shared memory.
    """
    if hasattr(memory, key):
        setattr(memory, key, value)
    else:
        raise AttributeError(f"'{key}' is not a valid memory field")

    return memory


def get_memory(memory: SharedMemory, key: str):
    """
    Retrieve a field from shared memory.
    """
    if hasattr(memory, key):
        return getattr(memory, key)

    raise AttributeError(f"'{key}' is not a valid memory field")