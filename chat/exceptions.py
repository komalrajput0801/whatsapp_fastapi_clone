from fastapi import status

from core.exceptions import CustomHTTPException


class RoomAlreadyExists(CustomHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Room with name already exists"


class RoomNotFound(CustomHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Room Not Found"
