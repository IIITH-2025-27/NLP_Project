"""
API Helper Functions
Utility functions for working with API endpoints
"""

from typing import Dict, Optional
from .endpoints import BASE_URL
from .schemas import ENDPOINTS


def get_full_url(endpoint_path: str, base_url: str = BASE_URL) -> str:
    """
    Get full URL for an endpoint
    
    Args:
        endpoint_path: The endpoint path (e.g., '/auth/login')
        base_url: Base URL of the API (default: BASE_URL constant)
        
    Returns:
        Full URL string
        
    Example:
        >>> get_full_url('/auth/login')
        'http://localhost:8000/auth/login'
    """
    return f"{base_url}{endpoint_path}"


def list_all_endpoints() -> Dict[str, dict]:
    """
    List all available endpoints with their details
    
    Returns:
        Dictionary of all endpoints
        
    Example:
        >>> endpoints = list_all_endpoints()
        >>> print(endpoints['auth_login'])
    """
    return {name: info for name, info in ENDPOINTS.items()}


def get_endpoint_info(endpoint_name: str) -> Optional[dict]:
    """
    Get detailed information about a specific endpoint
    
    Args:
        endpoint_name: Name of the endpoint (e.g., 'auth_login')
        
    Returns:
        Endpoint information dictionary or None if not found
        
    Example:
        >>> info = get_endpoint_info('auth_login')
        >>> print(info['method'])
        'POST'
    """
    return ENDPOINTS.get(endpoint_name, None)


def get_endpoints_by_method(method: str) -> Dict[str, dict]:
    """
    Get all endpoints for a specific HTTP method
    
    Args:
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        
    Returns:
        Dictionary of endpoints that use the specified method
        
    Example:
        >>> post_endpoints = get_endpoints_by_method('POST')
        >>> for name, info in post_endpoints.items():
        ...     print(f"{name}: {info['path']}")
    """
    return {
        name: info 
        for name, info in ENDPOINTS.items() 
        if info["method"] == method.upper()
    }


def get_public_endpoints() -> Dict[str, dict]:
    """
    Get all endpoints that don't require authentication
    
    Returns:
        Dictionary of public endpoints
        
    Example:
        >>> public = get_public_endpoints()
        >>> for name, info in public.items():
        ...     print(f"{info['method']} {info['path']}")
    """
    return {
        name: info 
        for name, info in ENDPOINTS.items() 
        if not info.get("auth_required", False)
    }


def get_protected_endpoints() -> Dict[str, dict]:
    """
    Get all endpoints that require authentication
    
    Returns:
        Dictionary of protected endpoints
        
    Example:
        >>> protected = get_protected_endpoints()
        >>> for name, info in protected.items():
        ...     print(f"{info['method']} {info['path']}")
    """
    return {
        name: info 
        for name, info in ENDPOINTS.items() 
        if info.get("auth_required", False)
    }


def get_endpoints_by_tag(tag: str) -> Dict[str, dict]:
    """
    Get all endpoints related to a specific feature/tag
    
    Args:
        tag: Feature tag (e.g., 'auth', 'chat', 'message', 'analyze')
        
    Returns:
        Dictionary of endpoints matching the tag
        
    Example:
        >>> auth_endpoints = get_endpoints_by_tag('auth')
        >>> for name, info in auth_endpoints.items():
        ...     print(f"{name}: {info['path']}")
    """
    tag_lower = tag.lower()
    return {
        name: info 
        for name, info in ENDPOINTS.items() 
        if tag_lower in name.lower()
    }


def format_endpoint_path(path: str, **params) -> str:
    """
    Format endpoint path with dynamic parameters
    
    Args:
        path: Endpoint path with placeholders (e.g., '/chats/{chat_id}')
        **params: Keyword arguments for path parameters
        
    Returns:
        Formatted path string
        
    Example:
        >>> format_endpoint_path('/chats/{chat_id}', chat_id='123')
        '/chats/123'
        >>> format_endpoint_path('/chats/{chat_id}/messages', chat_id='abc123')
        '/chats/abc123/messages'
    """
    formatted_path = path
    for key, value in params.items():
        placeholder = f"{{{key}}}"
        if placeholder in formatted_path:
            formatted_path = formatted_path.replace(placeholder, str(value))
    return formatted_path


def print_endpoints_summary():
    """
    Print a formatted summary of all endpoints
    
    Example:
        >>> print_endpoints_summary()
    """
    print("=" * 80)
    print("LyricMind API Endpoints Summary")
    print("=" * 80)
    
    print("\n1. All Endpoints:")
    print("-" * 80)
    for name, info in ENDPOINTS.items():
        auth = "🔒" if info.get("auth_required") else "🔓"
        print(f"{auth} {info['method']:6} {info['path']:40} {info['description']}")
    
    print("\n2. Public Endpoints (No Authentication Required):")
    print("-" * 80)
    public = get_public_endpoints()
    for name, info in public.items():
        print(f"🔓 {info['method']:6} {info['path']:40} {info['description']}")
    
    print("\n3. Protected Endpoints (Authentication Required):")
    print("-" * 80)
    protected = get_protected_endpoints()
    for name, info in protected.items():
        print(f"🔒 {info['method']:6} {info['path']:40} {info['description']}")
    
    print("\n" + "=" * 80)
    print(f"Total Endpoints: {len(ENDPOINTS)}")
    print(f"Public: {len(public)} | Protected: {len(protected)}")
    print("=" * 80)


def get_curl_example(endpoint_name: str, **params) -> str:
    """
    Generate a curl command example for an endpoint
    
    Args:
        endpoint_name: Name of the endpoint
        **params: Path parameters if needed
        
    Returns:
        Curl command string
        
    Example:
        >>> print(get_curl_example('auth_login'))
    """
    info = get_endpoint_info(endpoint_name)
    if not info:
        return f"Endpoint '{endpoint_name}' not found"
    
    path = info['path']
    if params:
        path = format_endpoint_path(path, **params)
    
    url = get_full_url(path)
    method = info['method']
    
    if method == 'GET':
        curl = f"curl -X GET '{url}'"
    else:
        curl = f"curl -X {method} '{url}' \\\n  -H 'Content-Type: application/json'"
        
        if info.get('auth_required'):
            curl += " \\\n  -H 'Authorization: Bearer YOUR_TOKEN'"
        
        if info.get('request_body') and isinstance(info['request_body'], dict):
            curl += " \\\n  -d '{\"key\": \"value\"}'"
    
    return curl


# ============================================================================
# MAIN - For Testing/Demonstration
# ============================================================================

if __name__ == "__main__":
    print_endpoints_summary()
    
    print("\n\nExample Usage:")
    print("-" * 80)
    
    print("\n1. Get endpoint info:")
    info = get_endpoint_info('auth_login')
    print(f"Login endpoint: {info['method']} {info['path']}")
    
    print("\n2. Format dynamic path:")
    chat_path = format_endpoint_path('/chats/{chat_id}', chat_id='abc123')
    print(f"Formatted path: {chat_path}")
    
    print("\n3. Get full URL:")
    full_url = get_full_url('/auth/login')
    print(f"Full URL: {full_url}")
    
    print("\n4. Curl example:")
    print(get_curl_example('auth_login'))
