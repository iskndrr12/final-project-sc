from flask import request, Blueprint
from utils import run_query
from flask_jwt_extended import get_jwt_identity, jwt_required


sales_bp = Blueprint("sales", __name__, url_prefix="/sales")

@sales_bp.route('', methods=['GET'])
@jwt_required()
def get_total_sales():
    user = get_jwt_identity()
    resp = run_query(f"select revenue as total from seller_revenue where user_id = '{user}'")

    return {'data': resp[0]}, 200