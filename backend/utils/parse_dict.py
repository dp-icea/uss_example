from typing import Any, Dict, List
from pydantic import BaseModel

def parse_dict(data: Dict | List, k: str) -> Any:
    """
    Recursively search for a key in a nested dictionary and return its value.
    
    Args:
        data (dict): The dictionary to search.
        k (str): The key to search for.
    
    Returns:
        Any: The value associated with the first occurrence of the key, or None if not found.
    """

    if isinstance(data, dict):
        if k in data:
            return data[k]
        for v in data.values():
            result = parse_dict(v, k)
            if result is not None:
                return result
    elif isinstance(data, list):
        for item in data:
            result = parse_dict(item, k)
            if result is not None:
                return result
    return None
