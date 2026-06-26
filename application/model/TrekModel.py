from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum
from application.db.db import db


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
    closed="closed"
    complete="complete"

class UserTable(db.Model):
    # User id || Username || Password || Type of User
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(), unique=True, nullable=False)
    type_of_user = db.Column(
        db.Enum(Role, native_enum=False, create_constraint=True, validate_strings=True),
        nullable=False,
    )
    def to_dict(self):
        return {
            "id": self.user_id,
            "user_name": self.user_name,
            "password": self.password,
            "type_of_user": self.type_of_user,
        }
    
class TrekTable(UserTable):
    # Trek ID || Trek Name || Location || Difficulty (Easy / Moderate / Hard) || Duration (in days) || Available Slots || Assigned Slot || Assigned Staff ID || Status (Pending / Approved / Open / Closed / Completed) || Start Date || End Date
    trek_id = db.Column(db.Integer,primary_key=True)
    trek_name = db.Column(db.String(),nullable=False)
    location = db.Column(db.String(),nullable=False)
    difficulty = db.Column(
        db.Enum(Difficulty, native_enum=False, create_constraint=True, validate_strings=True),
        nullable=False,
    )
    duration = db.Column(db.Integer,nullable=False)
    available_slots = db.Column(db.String(),nullable=False)
    assigned_slot = db.Column(db.String())
    assigned_staff_id = db.Column(db.Integer,nullable=False)
    status = db.Column(
        db.Enum(Status, native_enum=False, create_constraint=True, validate_strings=True),
        nullable=False,
    )
    # while writing code remember to add a valdiation that is given as an error in the FE 
    # to enter the correct date and time format so that evaluator can check it properly 
    start_date=db.Column(db.String())
    end_date=db.Column(db.String())
    