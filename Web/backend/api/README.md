# API Package

This package contains all API endpoint definitions and helper functions for the LyricMind backend.

## Structure

```
api/
├── __init__.py      # Package initialization with exports
├── endpoints.py     # API endpoint path constants
├── schemas.py       # Request/response schemas and endpoint details
├── helpers.py       # Helper functions for working with endpoints
└── README.md        # This file
```

## Files

### 1. `endpoints.py`
Contains API endpoint path constants:
- Base URL
- Authentication paths
- Analysis paths
- Chat and message paths

### 2. `schemas.py`
Contains detailed endpoint schemas:
- Request/response structures
- HTTP methods
- Authentication requirements
- Endpoint descriptions

### 3. `helpers.py`
Utility functions for working with endpoints:
- `get_full_url()` - Get complete URL for an endpoint
- `get_endpoint_info()` - Get details about a specific endpoint
- `get_endpoints_by_method()` - Filter by HTTP method
- `get_public_endpoints()` - Get endpoints without auth
- `get_protected_endpoints()` - Get endpoints requiring auth
- `format_endpoint_path()` - Format paths with dynamic parameters
- `get_curl_example()` - Generate curl command examples
- `print_endpoints_summary()` - Display all endpoints

## Usage

### Import endpoints

```python
from api import AUTH_LOGIN, ANALYZE_TEXT, GET_CHATS
from api.endpoints import ENDPOINTS

# Use in your code
login_path = AUTH_LOGIN  # '/auth/login'
```

### Use schemas

```python
from api.schemas import ENDPOINTS

# Get endpoint schema
login_schema = ENDPOINTS['auth_login']
print(login_schema['method'])  # 'POST'
print(login_schema['auth_required'])  # False
print(login_schema['request_body'])  # {'email': 'string', 'password': 'string'}
```

### Use helper functions

```python
from api.helpers import get_full_url, get_endpoint_info, get_public_endpoints

# Get full URL
full_url = get_full_url('/auth/login')
# 'http://localhost:8000/auth/login'

# Get endpoint details
info = get_endpoint_info('auth_login')
print(info['method'])  # 'POST'
print(info['auth_required'])  # False

# Get all public endpoints
public = get_public_endpoints()
for name, info in public.items():
    print(f"{info['method']} {info['path']}")
```

### Format dynamic paths

```python
from api.helpers import format_endpoint_path

# Format path with parameters
chat_path = format_endpoint_path('/chats/{chat_id}', chat_id='abc123')
# '/chats/abc123'

message_path = format_endpoint_path(
    '/chats/{chat_id}/messages', 
    chat_id='xyz789'
)
# '/chats/xyz789/messages'
```

### Generate curl examples

```python
from api.helpers import get_curl_example

# Get curl command
curl = get_curl_example('auth_login')
print(curl)
# curl -X POST 'http://localhost:8000/auth/login' \
#   -H 'Content-Type: application/json' \
#   -d '{"key": "value"}'
```

## Available Endpoints

### Authentication (Public)
- `POST /auth/request-otp` - Request OTP for signup
- `POST /auth/verify-otp` - Verify OTP and complete signup
- `POST /auth/resend-otp` - Resend OTP to email
- `POST /auth/signup` - Legacy signup (no OTP)
- `POST /auth/login` - Login with credentials

### Analysis (Protected)
- `POST /analyze` - Analyze text and generate lyrics
- `POST /analyze-image` - Analyze image emotion and generate lyrics

### Chats (Protected)
- `GET /chats` - Get all chats
- `POST /chats` - Create new chat
- `GET /chats/{chat_id}` - Get specific chat
- `PUT /chats/{chat_id}` - Update chat
- `DELETE /chats/{chat_id}` - Delete chat

### Messages (Protected)
- `GET /chats/{chat_id}/messages` - Get all messages
- `POST /chats/{chat_id}/messages` - Create message
- `DELETE /messages/{message_id}` - Delete message

## Testing

Run the helpers module directly to see all endpoints:

```bash
cd /path/to/backend
python3 -m api.helpers
```

This will display:
- Complete list of all endpoints
- Public vs protected endpoints
- Total endpoint couschema in `schemas.py`:
   ```python
   from .endpoints import NEW_ENDPOINT
   age

## Updating Endpoints

When adding new endpoints:

1. Add the path constant in `endpoints.py`:
   ```python
   NEW_ENDPOINT = "/new/path"
   ```

2. Add the endpoint details to the `ENDPOINTS` dictionary:
   ```python
   ENDPOINTS = {
       "new_endpoint": {
           "path": NEW_ENDPOINT,
           "method": "POST",
           "auth_required": True,
           "description": "Description",
           "request_body": {...},
           "response": {...}
       }
   }
   ```

3. Export it in `__init__.py` if needed:
   ```python
   from .endpoints import NEW_ENDPOINT
   __all__ = [..., 'NEW_ENDPOINT']
   ```

## Notes

- All protected endpoints require a valid JWT token in the Authorization header
- Public endpoints are available without authentication
- Path parameters are denoted with curly braces: `{param_name}`
- Use helper functions to work with dynamic paths instead of string concatenation
