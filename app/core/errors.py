from fastapi import HTTPException, status


class AuthenticationRequired(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")


class PolicyBlocked(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="Request blocked by policy")
