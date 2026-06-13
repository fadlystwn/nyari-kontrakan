import os
import random
from typing import Optional

def get_random_proxy() -> Optional[str]:
    """
    Select and return a random proxy string from the PROXY_LIST environment variable.
    Returns None if proxy list is empty or not configured.
    """
    proxy_list_raw = os.getenv("PROXY_LIST", "")
    if not proxy_list_raw:
        return None
    proxies = [p.strip() for p in proxy_list_raw.split(",") if p.strip()]
    return random.choice(proxies) if proxies else None
