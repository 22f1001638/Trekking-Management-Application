from datetime import datetime
from sqlalchemy import or_

from backend.dao.trek_dao import DAO
from backend.dao.create_trek_dao import CreateTrekDao
from backend.db.db import db
from backend.model.TrekModel import UserTable, Role, TrekTable, Status, Difficulty, BookingTable
from backend.service.booking_service import BookingService

class TrekAdminService:
    def __init__(self):
        self.user_dao = DAO()
        self.trek_dao = CreateTrekDao()

    def _check_admin(self, admin_id):
        admin = self.user_dao.get_by_id(admin_id)
        if not admin or admin.type_of_user != Role.admin or not admin.is_active:
            return None
        return admin

    def register_staff(self, data, user_id):
        admin = self._check_admin(user_id)
        if not admin:
            return {"message": "Unauthorized"}, 403

        if not data.get("username") or not data.get("password") or not data.get("email_id"):
            return {"message": "username, password, and email_id are required."}, 400

        if self.user_dao.get_by_username(data["username"]):
            return {"message": "Staff username already exists."}, 409

        new_staff = UserTable(
            user_name=data["username"],
            email_id=data["email_id"],
            password=data["password"],
            phone_num=data.get("phone_num"),
            type_of_user=Role.staff,
            is_active=True,
        )
        self.user_dao.save(new_staff)
        return new_staff.to_dict()

    def get_all_staff(self, admin_id=None):
        if admin_id is not None and not self._check_admin(admin_id):
            return {"message": "Unauthorized"}, 403
        return [user.to_dict() for user in self.user_dao.get_staff_list()]

    def get_user_list(self, admin_id=None):
        if admin_id is not None and not self._check_admin(admin_id):
            return {"message": "Unauthorized"}, 403
        return [user.to_dict() for user in self.user_dao.get_user_list()]

    def get_admin_dashboard(self, admin_id):
        admin = self._check_admin(admin_id)
        if not admin:
            return {"message": "Unauthorized"}, 403

        total_treks = TrekTable.query.count()
        total_users = UserTable.query.filter_by(type_of_user=Role.user).count()
        total_staff = UserTable.query.filter_by(type_of_user=Role.staff).count()
        total_bookings = BookingTable.query.count()

        return {
            "total_treks": total_treks,
            "total_users": total_users,
            "total_staff": total_staff,
            "total_bookings": total_bookings,
        }

    def assign_staff_to_trek(self, admin_id, trek_id, staff_id):
        admin = self._check_admin(admin_id)
        if not admin:
            return {"message": "Unauthorized"}, 403

        trek = self.trek_dao.get_by_id(trek_id)
        if not trek:
            return {"message": "Trek not found."}, 404

        staff = self.user_dao.get_by_id(staff_id)
        if not staff or staff.type_of_user != Role.staff or not staff.is_active:
            return {"message": "Assigned staff must be an active staff user."}, 400

        trek.assigned_staff_id = staff_id
        db.session.commit()
        return trek.to_dict()

    def get_all_bookings(self, admin_id):
        admin = self._check_admin(admin_id)
        if not admin:
            return {"message": "Unauthorized"}, 403
        return BookingService().get_all_booking()

    def get_trek_bookings(self, admin_id, trek_id):
        admin = self._check_admin(admin_id)
        if not admin:
            return {"message": "Unauthorized"}, 403

        trek = self.trek_dao.get_by_id(trek_id)
        if not trek:
            return {"message": "Trek not found."}, 404

        return [booking.to_dict() for booking in BookingTable.query.filter_by(trek_id=trek_id).all()]

    def _check_active_user(self, user_id):
        user = self.user_dao.get_by_id(user_id)
        if not user or not user.is_active:
            return None
        return user

    def search_treks(self, user_id, query=None, status=None, difficulty=None):
        user = self._check_active_user(user_id)
        if not user:
            return {"message": "Unauthorized"}, 403

        filters = []
        if query:
            query_filter = f"%{query}%"
            filters.append(or_(
                TrekTable.trek_name.ilike(query_filter),
                TrekTable.location.ilike(query_filter)
            ))
        if status:
            try:
                status_enum = Status(status.lower())
                filters.append(TrekTable.status == status_enum)
            except ValueError:
                pass
        if difficulty:
            try:
                diff_enum = Difficulty(difficulty.lower())
                filters.append(TrekTable.difficulty == diff_enum)
            except ValueError:
                pass

        if not filters:
            return [trek.to_dict() for trek in self.trek_dao.get_all()]

        query_obj = TrekTable.query
        for f in filters:
            query_obj = query_obj.filter(f)

        return [trek.to_dict() for trek in query_obj.all()]

    def search_users(self, admin_id, query):
        admin = self._check_admin(admin_id)
        if not admin:
            return {"message": "Unauthorized"}, 403

        if not query:
            return [user.to_dict() for user in UserTable.query.all()]

        users = UserTable.query.filter(
            or_(
                UserTable.user_name.ilike(f"%{query}%"),
                UserTable.email_id.ilike(f"%{query}%")
            )
        ).all()
        return [user.to_dict() for user in users]

    def search_staff(self, admin_id, query):
        admin = self._check_admin(admin_id)
        if not admin:
            return {"message": "Unauthorized"}, 403

        if not query:
            return [user.to_dict() for user in self.user_dao.get_staff_list()]

        staff = UserTable.query.filter(
            UserTable.type_of_user == Role.staff,
            or_(
                UserTable.user_name.ilike(f"%{query}%"),
                UserTable.email_id.ilike(f"%{query}%")
            )
        ).all()
        return [user.to_dict() for user in staff]

    def update_trek(self, admin_id, trek_id, updates):
        admin = self._check_admin(admin_id)
        if not admin:
            return {"message": "Unauthorized"}, 403

        trek = self.trek_dao.get_by_id(trek_id)
        if not trek:
            return {"message": "Trek not found."}, 404

        if "available_slots" in updates:
            try:
                trek.available_slots = int(updates["available_slots"])
            except (TypeError, ValueError):
                return {"message": "available_slots must be a number."}, 400

        if "status" in updates:
            trek.status = Status(updates["status"].lower())

        if "assigned_staff_id" in updates:
            staff = self.user_dao.get_by_id(updates["assigned_staff_id"])
            if not staff or staff.type_of_user != Role.staff or not staff.is_active:
                return {"message": "Assigned staff must be an active staff user."}, 400
            trek.assigned_staff_id = updates["assigned_staff_id"]

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

    def deactivate_user(self, admin_id, target_user_id):
        admin = self._check_admin(admin_id)
        if not admin:
            return {"message": "Unauthorized"}, 403

        target = self.user_dao.get_by_id(target_user_id)
        if not target:
            return {"message": "User not found."}, 404

        target.is_active = False
        self.user_dao.save(target)
        return {"message": "User deactivated.", "user": target.to_dict()}

    def activate_user(self, admin_id, target_user_id):
        admin = self._check_admin(admin_id)
        if not admin:
            return {"message": "Unauthorized"}, 403

        target = self.user_dao.get_by_id(target_user_id)
        if not target:
            return {"message": "User not found."}, 404

        target.is_active = True
        self.user_dao.save(target)
        return {"message": "User activated.", "user": target.to_dict()}