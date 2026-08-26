from fastapi import HTTPException, status


class AuthenticationRequired(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")


# super: Call the __init__() method of the parent class (HTTPException) and give it these values.
# just similiar to HTTPException(status_code=401, detail="Authentication required")
class PolicyBlocked(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="Request blocked by policy")
