from flask import request,jsonify,Blueprint
from utils import run_query
from flask_jwt_extended import jwt_required, get_jwt_identity

user_bp = Blueprint("user", __name__, url_prefix="/user")
@user_bp.route("", methods = ['GET'])
@jwt_required()
def User_details():
    # token = request.headers.get('token')
    user_id = get_jwt_identity() #identifikasi user berdasarkan id 

    user_info = run_query(f"SELECT name, email, phone_number FROM users WHERE id = '{user_id}' ")
    return {"data": user_info[0] }, 200

