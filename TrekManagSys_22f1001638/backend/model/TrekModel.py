from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum
from backend.db.db import db


class Role(enum.Enum):
    admin = "admin"
    staff = "staff"
    user = "user"

class Difficulty(enum.Enum):
    easy="easy"
    moderate="moderate"
    hard="hard"

class Status(enum.Enum):
    pending="pending"
    approved="approved"
    open="open"
    started="started"
    closed="closed"
    complete="complete"
class BookingStatus(enum.Enum):
    # Booked / Cancelled / Completed
    booked="booked"
    cancelled="cancelled"
    completed="completed"

class UserTable(db.Model):
    # User id || Username || Password || Type of User
    user_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    user_name = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    type_of_user = db.Column(
        db.Enum(Role, native_enum=False, create_constraint=True, validate_strings=True),
        nullable=False,
    )
    email_id = db.Column(db.String(), unique=True, nullable=True)
    phone_num = db.Column(db.String(), unique=True, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "id": self.user_id,
            "user_name": self.user_name,
            "type_of_user": self.type_of_user.value if self.type_of_user else None,
            "email_id": self.email_id,
            "phone_num": self.phone_num,
            "is_active": self.is_active,
        }
    
class TrekTable(db.Model):
    # Trek ID || Trek Name || Location || Difficulty (Easy / Moderate / Hard) || Duration (in days) || Available Slots || Assigned Slot || Assigned Staff ID || Status (Pending / Approved / Open / Closed / Completed) || Start Date || End Date
    trek_id = db.Column(db.Integer,primary_key=True)
    trek_name = db.Column(db.String(),nullable=False)
    price = db.Column(db.Float, nullable=False, default=0.0)
    location = db.Column(db.String(),nullable=False)
    difficulty = db.Column(
        db.Enum(Difficulty, native_enum=False, create_constraint=True, validate_strings=True),
        nullable=False,
    )
    duration = db.Column(db.Integer,nullable=False)
    available_slots = db.Column(db.Integer,nullable=False)
    assigned_slot = db.Column(db.String())
    assigned_staff_id = db.Column(db.Integer, nullable=True)
    status = db.Column(
        db.Enum(Status, native_enum=False, create_constraint=True, validate_strings=True),
        nullable=False,
    )
    start_date=db.Column(db.String())
    end_date=db.Column(db.String())

    def to_dict(self):
        return {
            "trek_id": self.trek_id,
            "trek_name": self.trek_name,
            "price": self.price,
            "location": self.location,
            "difficulty": self.difficulty.value if self.difficulty else None,
            "duration": self.duration,
            "available_slots": self.available_slots,
            "assigned_slot": self.assigned_slot,
            "assigned_staff_id": self.assigned_staff_id,
            "status": self.status.value if self.status else None,
            "start_date": self.start_date,
            "end_date": self.end_date,
        }

class BookingTable(db.Model):
    booking_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    user_id=db.Column(db.Integer,db.ForeignKey("user_table.user_id"),nullable=False)
    trek_id=db.Column(db.Integer,db.ForeignKey("trek_table.trek_id"),nullable=False)
    booking_date=db.Column(db.String())
    status=db.Column(db.Enum(BookingStatus,native_enum=False,create_constraint=True,validate_strings=True),nullable=False)
    payment_status=db.Column(db.String(), nullable=False, default='pending')

    def to_dict(self):
        return {
            "booking_id": self.booking_id,
            "user_id": self.user_id,
            "trek_id": self.trek_id,
            "booking_date": self.booking_date,
            "status": self.status.value if self.status else None,
            "payment_status": self.payment_status,
        }






