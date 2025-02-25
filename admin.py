from fastapi.requests import Request
from sqladmin import ModelView, Admin
from sqladmin.authentication import AuthenticationBackend

from config import settings
from database import SessionLocal, engine
from user.models import User


# This page will implement the authentication for your admin panel
class AdminAuth(AuthenticationBackend):

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        session = SessionLocal()
        user = session.query(User).filter(User.username == username).first()
        if user and password == user.password and user.is_admin:
            # TODO: check more about how does the authentication backend work
            request.session.update({"token": user.username})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        return token is not None


# create a view for your models
class UsersAdmin(ModelView, model=User):
    column_list = [
        'email', 'full_name', 'is_admin'
    ]

# # add the views to admin
def create_admin(app):
    authentication_backend = AdminAuth(secret_key=settings.ADMIN_SECRET_KEY)
    admin = Admin(app=app, engine=engine, authentication_backend=authentication_backend)
    admin.add_view(UsersAdmin)
    return admin
