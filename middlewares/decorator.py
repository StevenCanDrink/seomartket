import requests
from typing import Dict, Any, Callable, TypeVar
from functools import wraps
from fastapi import HTTPException

# Type variable for generic typing
T = TypeVar("T")


# 1. First define the custom HTTPError class
class HTTPError(Exception):
    """Custom HTTP error exception class"""

    def __init__(
        self, status_code: int, message: str, response=None, original_error=None
    ):
        self.status_code = status_code
        self.message = message
        self.response = response
        self.original_error = original_error
        super().__init__(self.message)

    def __str__(self):
        return f"HTTP {self.status_code}: {self.message}"


# 2. Then define the decorator that uses HTTPError
def handle_http_errors(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to handle HTTP errors and non-200 status codes
    """

    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            result = await func(*args, **kwargs)
            # If the result is a response object
            if hasattr(result, "status_code"):
                if result.status_code != 200:
                    result_json = result.json()
                    message = result_json.get("Message") or result_json.get("message")
                    raise HTTPError(
                        status_code=result.status_code,
                        message=message,
                    )
                # Auto-convert to JSON if it's a successful response
                try:
                    return result.json()
                except:
                    return result

            return result

        except requests.exceptions.RequestException as e:
            raise HTTPError(
                status_code=500, message=f"Network error: {str(e)}", original_error=e
            )
        except HTTPError:
            raise  # Re-raise our custom HTTP errors
        except Exception as e:
            raise HTTPError(
                status_code=500, message=f"Unexpected error: {str(e)}", original_error=e
            )

    return wrapper


def handle_exceptions(func: Callable) -> Callable:
    """
    Decorator to automatically handle exceptions and raise HTTPException
    with appropriate status codes and messages.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            # Re-raise HTTPException as is
            raise
        except Exception as e:
            # Handle Bunny-specific exceptions or general exceptions
            if hasattr(e, "status_code") and hasattr(e, "message"):
                raise HTTPException(status_code=e.status_code, detail=e.message)
            else:
                # For unexpected errors, you might want to log them
                # and return a generic error response
                raise HTTPException(status_code=500, detail="Internal server error")

    return wrapper


def supa_handle_exceptions(func: Callable) -> Callable:
    """
    Decorator to automatically handle exceptions and raise HTTPException
    with appropriate status codes and messages.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            raise
        except Exception as e:
            print(e)
            # Re-raise HTTPException as is
            if hasattr(e, "message"):
                raise HTTPException(status_code=400, detail=e.message or e)
            else:
                # For unexpected errors, you might want to log them
                # and return a generic error response
                raise HTTPException(status_code=500, detail="Internal server error")

    return wrapper
