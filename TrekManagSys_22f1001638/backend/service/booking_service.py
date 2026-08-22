from datetime import datetime
from flask import jsonify
from backend.dao.trek_dao import DAO
from backend.db.db import db
from backend.model.TrekModel import Role, BookingTable, BookingStatus, Status

from backend.dao.create_trek_dao import CreateTrekDao
from backend.dao.booking_dao import BookingDao

class BookingService:
    def __init__(self):
        self.user_dao = DAO()
        self.trek_dao = CreateTrekDao()
        self.book_dao = BookingDao()

    def book_trek(self, book_object):
        user = self.user_dao.get_by_id(book_object.get("user_id"))
        if not user or user.type_of_user != Role.user or not user.is_active:
            return {"message": "Unauthorized or inactive user."}, 403

        trek = self.trek_dao.get_by_id(book_object.get("trek_id"))
        if not trek:
            return {"message": "Trek not found."}, 404

        if trek.status != Status.open:
            return {"message": "Trek is not open for booking."}, 400

        if trek.available_slots <= 0:
            return {"message": "No available slots left."}, 400

        existing = self.book_dao.get_booking_by_user_and_trek(user.user_id, trek.trek_id)
        if existing:
            return {"message": "Duplicate booking is not allowed."}, 409

        if "booking_date" not in book_object or not book_object["booking_date"]:
            book_object["booking_date"] = datetime.now().strftime("%Y-%m-%d")
        
        if "status" not in book_object or not book_object["status"]:
            book_object["status"] = BookingStatus.booked

        book = BookingTable(**book_object)
        self.book_dao.save(book)

        trek.available_slots = trek.available_slots - 1
        db.session.commit()

        return book.to_dict()

    def get_all_booking(self):
        bookings = self.book_dao.get_all_booking()
        return [self._booking_to_dict(b) for b in bookings]

    def get_booking_history_by_user(self, user_id):
        user = self.user_dao.get_by_id(user_id)
        if not user or not user.is_active:
            return {"message": "Unauthorized"}, 403

        bookings = self.book_dao.get_booking_by_user_id(user_id)
        return jsonify([self._booking_to_dict(b) for b in bookings])

    def _booking_to_dict(self, booking):
        data = booking.to_dict()
        trek = self.trek_dao.get_by_id(booking.trek_id)
        if trek:
            data["trek_name"] = trek.trek_name
            data["trek_status"] = trek.status.value if trek.status else None
        user = self.user_dao.get_by_id(booking.user_id)
        if user:
            data["user_name"] = user.user_name
        return data