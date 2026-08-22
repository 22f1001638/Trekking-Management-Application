from flask import Blueprint
from flask import jsonify
from flask import request
from flask import current_app
from sqlalchemy import or_
from backend.dao.trek_dao import DAO
from backend.model.TrekModel import UserTable
from backend.service.login_service import LoginService
from backend.service.create_trek_service import CreateTrekService
from backend.service.trek_admin_service import TrekAdminService
from backend.service.trek_staff_service import TrekStaffService
from backend.service.booking_service import BookingService
from backend.jobs import send_daily_reminders, generate_monthly_report, export_booking_history, get_export_status, get_export_file
# from application.controllers.user_controller import UserController

user_bp = Blueprint(
    "users",
    __name__,
    url_prefix="/users"
)

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    return LoginService().validate_login(data)

@user_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    return LoginService().register(data)

@user_bp.route("/get_all_staff/<admin_id>", methods=["GET"])
def get_all_staff(admin_id):
    return TrekAdminService().get_all_staff(admin_id)

@user_bp.route("/get_all_users/<admin_id>", methods=["GET"])
def get_all_users(admin_id):
    return TrekAdminService().get_user_list(admin_id)

@user_bp.route("/get_assigned_treks/<user_id>", methods=["GET"])
def assigned_treks(user_id):
    return TrekStaffService().assigned_treks(user_id=user_id)

@user_bp.route("/get_trek", methods=["GET"])
def get_trek():
    return CreateTrekService().get_all_trek()

@user_bp.route("/create_trek/<user_id>",methods=["POST"])
def create_trek(user_id):
    data = request.get_json() or {}
    print(data)
    return CreateTrekService().create_trek(user_id, trek_object=data)

@user_bp.route("/register_staff/<user_id>", methods=["POST"])
def register_staff(user_id):
    data = request.get_json() or {}
    return TrekAdminService().register_staff(data, user_id)

@user_bp.route("/deactivate_user/<admin_id>/<target_user_id>", methods=["POST"])
def deactivate_user(admin_id, target_user_id):
    return TrekAdminService().deactivate_user(admin_id, target_user_id)

@user_bp.route("/activate_user/<admin_id>/<target_user_id>", methods=["POST"])
def activate_user(admin_id, target_user_id):
    return TrekAdminService().activate_user(admin_id, target_user_id)

@user_bp.route("/admin_dashboard/<admin_id>", methods=["GET"])
def admin_dashboard(admin_id):
    return TrekAdminService().get_admin_dashboard(admin_id)

@user_bp.route("/get_all_bookings/<admin_id>", methods=["GET"])
def get_all_bookings(admin_id):
    return TrekAdminService().get_all_bookings(admin_id)

@user_bp.route("/get_trek_bookings/<admin_id>/<trek_id>", methods=["GET"])
def get_trek_bookings(admin_id, trek_id):
    return TrekAdminService().get_trek_bookings(admin_id, trek_id)

@user_bp.route("/search_users/<admin_id>", methods=["GET"])
def search_users(admin_id):
    query = request.args.get("q")
    return TrekAdminService().search_users(admin_id, query)

@user_bp.route("/search_staff/<admin_id>", methods=["GET"])
def search_staff(admin_id):
    query = request.args.get("q")
    return TrekAdminService().search_staff(admin_id, query)

@user_bp.route("/search_treks/<user_id>", methods=["GET"])
def search_treks(user_id):
    query = request.args.get("q")
    status = request.args.get("status")
    difficulty = request.args.get("difficulty")
    return TrekAdminService().search_treks(user_id, query, status, difficulty)

@user_bp.route("/assign_staff/<admin_id>/<trek_id>/<staff_id>", methods=["POST"])
def assign_staff(admin_id, trek_id, staff_id):
    return TrekAdminService().assign_staff_to_trek(admin_id, trek_id, staff_id)

@user_bp.route("/update_trek/<user_id>/<trek_id>", methods=["POST"])
def update_trek(user_id, trek_id):
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"message": "Invalid user id."}), 400

    try:
        trek_id = int(trek_id)
    except ValueError:
        return jsonify({"message": "Invalid trek id."}), 400

    data = request.get_json() or {}
    return TrekStaffService().update_trek(user_id, trek_id, data)

@user_bp.route("/create_booking",methods=["POST"])
def create_booking():
    data = request.get_json() or {}
    print(data)
    return BookingService().book_trek(data)

@user_bp.route("/get_booking",methods=["GET"])
def get_booking():
    return BookingService().get_all_booking()

@user_bp.route("/get_bookings/<user_id>", methods=["GET"])
def get_bookings(user_id):
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"message": "Invalid user id."}), 400
    return BookingService().get_booking_history_by_user(user_id)

@user_bp.route("/export_bookings/<user_id>", methods=["POST"])
def export_bookings(user_id):
    export_booking_history(int(user_id), current_app._get_current_object())
    return jsonify({"message": "Booking export requested."}), 202

@user_bp.route("/export_status/<user_id>", methods=["GET"])
def export_status(user_id):
    return jsonify({"status": get_export_status(int(user_id))})

@user_bp.route("/export_file/<user_id>", methods=["GET"])
def export_file(user_id):
    path = get_export_file(int(user_id))
    if not path:
        return jsonify({"message": "No export file found."}), 404
    return jsonify({"path": path})

@user_bp.route("/daily_reminders", methods=["GET"])
def daily_reminders():
    path = send_daily_reminders()
    return jsonify({"message": "Daily reminders generated.", "path": path})

@user_bp.route("/monthly_report", methods=["GET"])
def monthly_report():
    path = generate_monthly_report()
    return jsonify({"message": "Monthly report generated.", "path": path})

@user_bp.route("/edit_user", methods=["PATCH"])
def edit_user():

    data = request.get_json()

    print(data)
    print(type(data))

    email_id = data["email_id"]

    return DAO().edit_user(email_id, data)
    # return DAO().edit_user(email_id, data)
    # user = DAO().edit_user(user_id, data)
    # if not user:
    #     return {
    #         "message": "User not found"
    #     }, 404
    # return {
    #     "message": "User updated successfully",
    #     "user": user.to_dict()
    # }, 200