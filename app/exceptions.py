class APIException(Exception):
    status_code: int = 500
    detail: str = "An unexpected error occurred"
    code: str = "INTERNAL_ERROR"


class UserAlreadyExists(APIException):
    status_code = 409
    detail = "A user with this email already exists"
    code = "USER_ALREADY_EXISTS"


class InvalidCredentials(APIException):
    status_code = 401
    detail = "Invalid email or password"
    code = "INVALID_CREDENTIALS"


class InvalidCode(APIException):
    status_code = 400
    detail = "Invalid or already used activation code"
    code = "INVALID_CODE"


class CodeExpired(APIException):
    status_code = 410
    detail = "Activation code has expired"
    code = "CODE_EXPIRED"
