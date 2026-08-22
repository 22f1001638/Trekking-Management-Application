from backend.model.TrekModel import TrekTable
from backend.db.db import db


class CreateTrekDao:
    def __init__(self):
        pass

    def get_all(self):

        return TrekTable.query.all()

    def get_by_id(self, trek_id):

        return TrekTable.query.get(trek_id)
    
    def save(self, trek_object):
        print("trek_obj_dao",trek_object)

        db.session.add(trek_object)
        db.session.commit()

        return trek_object

    def get_staff_assigned_trek(self,assigned_staff_id):
        return TrekTable.query.filter_by(assigned_staff_id=assigned_staff_id)