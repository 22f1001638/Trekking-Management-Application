from backend.model.TrekModel import UserTable,Role
from backend.db.db import db


class DAO:
    def __init__(self):
        pass

    def get_all(self):

        return UserTable.query.all()

    def get_by_id(self, user_id):

        return UserTable.query.get(user_id)

    def get_by_username(self,user_name):
        # print("user_name_dao",user_name)
        # print("UserTable.query.get(user_name)",UserTable.query.filter_by(user_name=user_name).first())
        return UserTable.query.filter_by(user_name=user_name).first()

    def get_by_email(self, email):
        return UserTable.query.filter_by(email_id=email).first()

    def save(self, user):

        db.session.add(user)
        db.session.commit()

        return user

    def get_staff_list(self):
        return UserTable.query.filter_by(type_of_user=Role.staff)

    def get_user_list(self):
        return UserTable.query.filter_by(type_of_user=Role.user)

    def edit_user(self, email_id, data):
        user = UserTable.query.filter_by(
            email_id=email_id
        ).first()
        if not user:
            return {
                "message": "User not found"
            }, 404
        data.pop("email_id", None)
        for key, value in data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        db.session.commit()
        return {
            "message": "User updated successfully",
            "user": user.to_dict()
        }, 200