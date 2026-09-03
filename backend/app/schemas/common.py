from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Details of an error response."""

    code: str
    message: str


class ErrorResponse(BaseModel):
    """Standard error response wrapper."""

    error: ErrorDetail
