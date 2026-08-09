from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """
    Verify API key for authentication.
    If API_KEY is not configured in settings, authentication is disabled (for development).
    """
    configured_key = settings.api_key
    
    # If no API key is configured, allow access (development mode)
    if not configured_key:
        return True
    
    # If API key is configured but not provided, deny access
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key missing. Provide X-API-Key header."
        )
    
    # If API key doesn't match, deny access
    if api_key != configured_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key."
        )
    
    return True

async def verify_api_key_optional(api_key: str = Security(api_key_header)):
    """
    Optional API key verification - allows access even without key.
    Useful for endpoints that should work in both authenticated and public modes.
    """
    configured_key = settings.api_key
    
    # If no API key is configured, allow access
    if not configured_key:
        return True
    
    # If API key is provided, verify it
    if api_key and api_key != configured_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key."
        )
    
    return True