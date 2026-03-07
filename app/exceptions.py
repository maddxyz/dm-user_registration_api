class UserAlreadyExists(Exception):
    detail = "A user with this email already exists"
    code = "USER_ALREADY_EXISTS"
