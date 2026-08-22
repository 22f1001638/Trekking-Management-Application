import json
from datetime import datetime
from flask import current_app
from backend.dao.trek_dao import DAO

from backend.db.db import db
from backend.model.TrekModel import UserTable, Role, TrekTable, Difficulty, Status
from backend.dao.create_trek_dao import CreateTrekDao

CACHE_KEY = "treks_cache"
CACHE_TTL_SECONDS = 300

class CreateTrekService:
    def __init__(self):
        self.user_dao = DAO()
        self.create_dao = CreateTrekDao()

    def create_trek(self, user_id, trek_object):
        check = self.user_dao.get_by_id(user_id)
        if not check or check.type_of_user != Role.admin or not check.is_active:
            return {"message": "Unauthorized"}, 403

        # 1. Map payload key 'name' to model field 'trek_name' if needed
        if 'name' in trek_object and 'trek_name' not in trek_object:
            trek_object['trek_name'] = trek_object.pop('name')

        # 2. Convert string enums from JSON payload into actual Enum instances
        if 'difficulty' in trek_object and isinstance(trek_object['difficulty'], str):
            trek_object['difficulty'] = Difficulty(trek_object['difficulty'].lower())

        if 'status' in trek_object and isinstance(trek_object['status'], str):
            trek_object['status'] = Status(trek_object['status'].lower())

        if 'available_slots' in trek_object:
            try:
                trek_object['available_slots'] = int(trek_object['available_slots'])
            except (TypeError, ValueError):
                return {"message": "available_slots must be a number."}, 400

        if 'assigned_staff_id' in trek_object:
            staff = self.user_dao.get_by_id(trek_object['assigned_staff_id'])
            if not staff or staff.type_of_user != Role.staff or not staff.is_active:
                return {"message": "Assigned staff must be an active staff user."}, 400

        if 'start_date' in trek_object:
            try:
                datetime.strptime(trek_object['start_date'], "%Y-%m-%d")
            except ValueError:
                return {"message": "Invalid start_date format."}, 400

        if 'end_date' in trek_object:
            try:
                datetime.strptime(trek_object['end_date'], "%Y-%m-%d")
            except ValueError:
                return {"message": "Invalid end_date format."}, 400

        trek = TrekTable(**trek_object)
        self.create_dao.save(trek)

        return trek.to_dict()

    def get_all_trek(self):
        redis_client = None
        try:
            redis_client = current_app.redis_client
        except Exception:
            redis_client = None

        if redis_client:
            cached = redis_client.get(CACHE_KEY)
            if cached:
                return json.loads(cached)

        treks = [t.to_dict() for t in self.create_dao.get_all()]
        if redis_client:
            try:
                redis_client.setex(CACHE_KEY, CACHE_TTL_SECONDS, json.dumps(treks))
            except Exception:
                pass
        return treks

    def clear_cache(self):
        try:
            redis_client = current_app.redis_client
            if redis_client:
                redis_client.delete(CACHE_KEY)
        except Exception:
            pass