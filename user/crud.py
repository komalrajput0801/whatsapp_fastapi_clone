# Contains CRUD operations
from typing import Any, Dict, List, Union

from core.base_crud import CRUDBase
from sqlalchemy.orm import Session, column_property
from user.exceptions import UserAlreadyExists, UserNotFound
from user.models import User
from chat.models import room_members_table
from user.schemas import UserBase, UserIn, UserID, UserOut
from user.utils import get_hashed_password


class CRUDUser(CRUDBase[User, UserIn, UserIn]):
    def create(self, db: Session, obj_in: UserIn) -> User:
        db_user = db.query(User).filter(User.email == obj_in.email).first()
        if db_user:
            raise UserAlreadyExists()

        # hash the password before saving it to database
        obj_in.password = get_hashed_password(obj_in.password)
        return super().create(db, obj_in=obj_in)

    def get_user_by_username(self, db: Session, username: str) -> User:
        return db.query(User).filter(User.username == username).first()

    def get_multi(
        self, db: Session, page_size: int = 10, page_num: int = 1, search: str = None
    ) -> List[User]:
        if search:
            return (
                db.query(User)
                .filter(User.full_name.like(f"{search}%") | User.email.like(f"{search}%"))
                .offset((page_num - 1) * page_size)
                .limit(page_size)
                .all()
            )
        return super().get_multi(db, offset=(page_num - 1) * page_size, limit=page_size)

    def get_users_with_chat_room(self, db: Session, logged_in_user: User, search: str = None) -> List[User]:
        """
        Returns all users list along with chat room id if they have chat rooms with logged in user
        else None
        """

        # fetch all chat rooms of logged in user
        chat_rooms_sq = db.query(room_members_table.c.chat_room_id).filter(
            room_members_table.c.member_id == logged_in_user.id).subquery()

        # now we do outer join with user and room members table so it will return
        # those users who have chat room with logged in user and also return those
        # users who do not have chat room with logged in user as this is a outer join
        users_with_rooms = db.query(
            User, column_property(room_members_table.c.chat_room_id.label("chat_room_id"))
            ).filter(User.id != logged_in_user.id).outerjoin( # exclude logged in user from list
            room_members_table, (
                User.id == room_members_table.c.member_id) & (  # User.id represents id in each row of user
                room_members_table.c.chat_room_id.in_(chat_rooms_sq)
            )
        )
        if search:
            users_with_rooms = users_with_rooms.filter(User.full_name.like(f"{search}%") | User.email.like(f"{search}%"))
        return [
            UserOut.from_orm(user).copy(update={"chat_room_id": chat_room_id})
                for user, chat_room_id in users_with_rooms.all()
        ]

    def update(self, db: Session, user_id: UserID, obj_in: Union[UserBase, Dict[str, Any]]) -> User:
        db_user = db.query(User).get(user_id)
        if not db_user:
            raise UserNotFound()
        # checks if email passed in update data already exists
        # excluding the email of user obj
        user_exists = (
            db.query(User)
            .filter(User.email == obj_in.email)
            .filter(User.email != db_user.email)  # works as exclude
            .first()
        )
        if user_exists:
            raise UserAlreadyExists()
        return super().update(db, db_obj=db_user, obj_in=obj_in)


user = CRUDUser(User)
