from flask import jsonify
from flask_jwt_extended import create_access_token,JWTManager
from backend.dao.trek_dao import DAO
from backend.model.TrekModel import UserTable, Role

class LoginService:
    def __init__(self):
        # use an instance of the DAO to call instance methods
        self.user_dao = DAO()

    def validate_login(self, data):
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"message": "Username and password are required."}), 400

        user = self.user_dao.get_by_username(username)
        if not user or user.password != password:
            return jsonify({"message": "Invalid username or password."}), 401

        # determine role and include username + role as additional claims
        role_value = user.type_of_user.value if hasattr(user.type_of_user, 'value') else str(user.type_of_user)
        access_token = create_access_token(
            identity=str(user.user_id),
            additional_claims={"username": user.user_name, "role": role_value}
        )

        return jsonify({
            "message": "Login successful",
            "token": access_token,
            "user_id": user.user_id,
            "id": user.user_id,
            "username": user.user_name,
            "role": role_value,
            "is_active": user.is_active,
            "email_id": user.email_id,
            "phone_num": user.phone_num,
        }), 200
        # if user_role == Role.admin:
        #     return jsonify({"role": "admin"})
        # if user_role == Role.staff:
        #     return jsonify({"role": "staff"})
        # if user_role == Role.user:
        #     return jsonify({"role": "user"})

        # return jsonify({"message": "Unable to determine user role."}), 500

    def register(self, data):
        username = data.get("username")
        email_id = data.get("email_id")
        password = data.get("password")
        phone_num = data.get("phone_num")

        if not username or not email_id or not password or not phone_num:
            return jsonify({"message": "All registration fields are required."}), 400

        check = self.user_dao.get_by_username(username)
        if check:
            return jsonify({"message": "User already exists."}), 409

        user_data = {
            "user_name": username,
            "email_id": email_id,
            "password": password,
            "phone_num": phone_num,
            "type_of_user": Role.user
        }
        new_user = UserTable(**user_data)
        self.user_dao.save(new_user)

        return jsonify({"message": "Registration successful."}), 201
    

    # def get_all_trek(self):
    #     return self.create_dao.get_all()