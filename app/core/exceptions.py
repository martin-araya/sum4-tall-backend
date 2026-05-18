from typing import Any

class DomainError(Exception):
    """Base exception class for all domain-related errors."""
    code: str = "domain_error"
    status: int = 400

    def __init__(self, message: str, **ctx: Any) -> None:
        super().__init__(message)
        self.message = message
        self.ctx = ctx


class NotFound(DomainError):
    """Exception raised when a resource is not found."""
    code: str = "not_found"
    status: int = 404


class Conflict(DomainError):
    """Exception raised when a business conflict occurs."""
    code: str = "conflict"
    status: int = 409


class PermissionDenied(DomainError):
    """Exception raised when action is forbidden for user."""
    code: str = "permission_denied"
    status: int = 403


class AuthenticationError(DomainError):
    """Exception raised for login or token issues."""
    code: str = "authentication_error"
    status: int = 401
