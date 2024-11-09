from fastapi_utils.guid_type import GUID, GUID_SERVER_DEFAULT_POSTGRESQL
from sqlalchemy import Column, DateTime, func

from database import Base


class UUIDBase(Base):
    __abstract__ = True

    id = Column(GUID, primary_key=True, server_default=GUID_SERVER_DEFAULT_POSTGRESQL)


class TimestampMixin(object):
    created_at = Column(DateTime, default=func.now())
