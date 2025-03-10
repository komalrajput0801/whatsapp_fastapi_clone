from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials
from fastapi_utils.cbv import cbv
from sqlalchemy.orm import Session

from core.dependencies import common_parameters
from core.dependencies import get_db
from user.crud import user
from user.models import BlackListedToken
from user.schemas import UserIn, UserOut, UserID, UserUpdate
from user.utils import verify_password, create_access_token, get_current_user, security

router = APIRouter()

@cbv(router)
class UserCBV:
    session: Session = Depends(get_db)

    @router.get("/", response_model=List[UserOut])
    def get_users(self, common_params: dict = Depends(common_parameters)):
        return user.get_multi(
            self.session,
            page_num=common_params["page_num"],
            page_size=common_params["page_size"],
            search=common_params["search"],
        )

    @router.get("/chat-rooms/", response_model=List[UserOut])
    def get_users_with_chat_room(
        self, common_params: dict = Depends(common_parameters), logged_in_user=Depends(get_current_user)):
        return user.get_users_with_chat_room(
            self.session,
            logged_in_user,
            search=common_params["search"],
        )

    @router.post("/register/", response_model=UserOut)
    def register_user(self, user_schema: UserIn):
        return user.create(self.session, user_schema)

    @router.get("/{uuid}", response_model=UserOut)
    def get_user_by_uuid(self, user_id: UserID):
        return user.get(self.session, user_id)

    @router.put("/{user_id}", response_model=UserOut)
    def edit_user(self, user_id: UserID, update_data: UserUpdate):
        return user.update(self.session, user_id, update_data)

    @router.delete("/{user_id}")
    def remove_user(self, user_id: UserID):
        user.remove(self.session, id=user_id)
        return {"message": "User Deleted successfully"}

    @router.post("/login/")
    def user_login(self, form_data: OAuth2PasswordRequestForm = Depends()):
        user_in_db = user.get_user_by_username(self.session, form_data.username)
        if not user_in_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect username"
            )
        if not verify_password(form_data.password, user_in_db.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect password"
            )
        return {
            "access_token": create_access_token(user_in_db.username), 
            "token_type": "Bearer",
            "senderId": user_in_db.id
        }

    @router.post("/logout/")
    def user_logout(self, auth: HTTPAuthorizationCredentials = Depends(security)):
        token = auth.credentials
        if BlackListedToken.check_token_is_blacklisted_or_not(token):
            return {
                "message": "Token is already blacklisted"
            }
        BlackListedToken.blacklist(token)
        return {
            "message": "Logged out successfully"
        }
