from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response schema.
    """
    items: List[T]
    total: int
    page: int
    size: int

class SuccessResponse(BaseModel):
    """
    Generic success response schema.
    """
    message: str = "Operation successful"
    status_code: int = 200

class ErrorResponse(BaseModel):
    """
    Generic error response schema.
    """
    message: str = "Operation failed"
    status_code: int = 500
    detail: Optional[str] = None

class IDSchema(BaseModel):
    """
    Schema for returning a resource ID.
    """
    id: int
