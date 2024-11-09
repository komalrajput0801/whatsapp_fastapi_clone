from sqlalchemy.orm import Session

from fastapi.params import Query
from database import SessionLocal


# Dependency
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def common_parameters(
    page_num: int = Query(default=1, description="Page Number"),
    page_size: int = Query(default=10, description="Page Size"),
    search: str = Query(default=None, description="Search parameter")
):
    """Returns query parameters common to multiple endpoints"""
    return {"page_num": page_num, "page_size": page_size, "search": search}
