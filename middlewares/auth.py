# from functools import wraps
# from typing import Dict, Any, Callable, TypeVar, Optional, List
from fastapi import HTTPException, Request, Header
from auth.supabase import get_supabase
import jwt, json
import base64

# from auth.claim import JWTTokenManager
# import inspect


# # @auth_middleware(required_roles=["admin"])
# def auth_middleware(required_roles: Optional[List[str]] = None):
#     def decorator(func: Callable):
#         @wraps(func)
#         async def wrapper(request: Request, *args, **kwargs):
#             # Get token from Authorization header
#             auth_header = request.headers.get("Authorization")

#             if not auth_header:
#                 raise HTTPException(
#                     status_code=401, detail="Authorization header missing"
#                 )

#             try:
#                 scheme, token = auth_header.split()
#                 if scheme.lower() != "bearer":
#                     raise HTTPException(
#                         status_code=401, detail="Invalid authorization scheme"
#                     )
#             except ValueError:
#                 raise HTTPException(
#                     status_code=401, detail="Invalid authorization header format"
#                 )

#             token_manager = JWTTokenManager()

#             try:
#                 claim = token_manager.verify_token(token)

#                 # Check role authorization
#                 if (
#                     required_roles is not None
#                     and claim.get("role") not in required_roles
#                 ):
#                     raise HTTPException(
#                         status_code=403,
#                         detail=f"Insufficient permissions. Required: {required_roles}, Your role: {claim.get('role')}",
#                     )

#                 # Add user claim to kwargs
#                 kwargs["user"] = claim
#                 return await func(request, *args, **kwargs)

#             except HTTPException:
#                 raise
#             except Exception as e:
#                 raise HTTPException(status_code=500, detail="Authentication failed")

#         # Update function signature to include request parameter
#         sig = inspect.signature(func)
#         params = list(sig.parameters.values())
#         if not any(param.name == "request" for param in params):
#             params.insert(
#                 0,
#                 inspect.Parameter(
#                     "request",
#                     inspect.Parameter.POSITIONAL_OR_KEYWORD,
#                     annotation=Request,
#                 ),
#             )
#         wrapper.__signature__ = sig.replace(parameters=params)

#         return wrapper

#     return decorator


def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.split(" ")[1]

    # fix base64 padding
    def fix_padding(b64: str):
        return b64 + "=" * (-len(b64) % 4)

    parts = token.split(".")
    if len(parts) != 3:
        raise HTTPException(status_code=401, detail="Invalid JWT format")

    payload_bytes = base64.urlsafe_b64decode(fix_padding(parts[1]))
    payload = json.loads(payload_bytes.decode("utf-8"))

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    return user_id


def get_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    return authorization.split(" ")[1]


def get_supabase_client(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.split(" ")[1]
    return get_supabase().auth_session(token)
