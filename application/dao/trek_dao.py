from application.model.TrekModel import UserTable
from application.db.db import db


class DAO:
    def __init__(self):
        pass

    def get_all(self):

        return UserTable.query.all()

    def get_by_id(self, user_id):

        return UserTable.query.get(user_id)

    def save(self, user):

        db.session.add(user)
        db.session.commit()

        return user
