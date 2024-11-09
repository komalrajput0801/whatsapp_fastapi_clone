from fastapi import status

from core.exceptions import CustomHTTPException


class UserAlreadyExists(CustomHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "The user with this username already exists"


class UserNotFound(CustomHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "User not found with given id"
