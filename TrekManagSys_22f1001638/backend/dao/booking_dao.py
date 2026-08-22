from backend.model.TrekModel import BookingTable
from backend.db.db import db


class BookingDao:
    def __init__(self):
        pass

    def get_all_booking(self):
        return BookingTable.query.all()

    def get_booking_by_user_id(self, user_id):
        return BookingTable.query.filter_by(user_id=user_id).all()

    def get_booking_by_trek_id(self, trek_id):
        return BookingTable.query.filter_by(trek_id=trek_id).all()

    def get_booking_by_user_and_trek(self, user_id, trek_id):
        return BookingTable.query.filter_by(user_id=user_id, trek_id=trek_id).first()

    def save(self, booking):
        db.session.add(booking)
        db.session.commit()
        return booking