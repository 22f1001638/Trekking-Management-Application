from datetime import datetime
from backend.dao.trek_dao import DAO
from backend.db.db import db
from backend.model.TrekModel import Role, Status
from backend.dao.create_trek_dao import CreateTrekDao

class TrekStaffService:
    def __init__(self):
        self.user_dao = DAO()
        self.trek_dao = CreateTrekDao()

    def assigned_treks(self, user_id):
        user = self.user_dao.get_by_id(user_id)
        if not user or user.type_of_user != Role.staff or not user.is_active:
            return []
        return [trek.to_dict() for trek in self.trek_dao.get_staff_assigned_trek(user_id)]

    def update_trek(self, user_id, trek_id, updates):
        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            return {"message": "Invalid user id."}, 400

        try:
            trek_id = int(trek_id)
        except (TypeError, ValueError):
            return {"message": "Invalid trek id."}, 400

        user = self.user_dao.get_by_id(user_id)
        if not user or user.type_of_user != Role.staff or not user.is_active:
            return {"message": "Unauthorized"}, 403

        trek = self.trek_dao.get_by_id(trek_id)
        if not trek:
            return {"message": "Trek not found."}, 404

        if trek.assigned_staff_id != user_id:
            return {"message": "You can only update treks assigned to you."}, 403

        if "available_slots" in updates:
            try:
                trek.available_slots = int(updates["available_slots"])
            except (TypeError, ValueError):
                return {"message": "available_slots must be a number."}, 400

        if "status" in updates:
            trek.status = Status(updates["status"].lower())

        if "start_date" in updates:
            try:
                datetime.strptime(updates["start_date"], "%Y-%m-%d")
                trek.start_date = updates["start_date"]
            except ValueError:
                return {"message": "Invalid start_date format."}, 400

        if "end_date" in updates:
            try:
                datetime.strptime(updates["end_date"], "%Y-%m-%d")
                trek.end_date = updates["end_date"]
            except ValueError:
                return {"message": "Invalid end_date format."}, 400

        db.session.commit()
        return trek.to_dict()