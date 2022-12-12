from flask import request, Blueprint
from utils import run_query
from flask_jwt_extended import get_jwt_identity, jwt_required

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')

@orders_bp.route('', methods=['GET'])
@jwt_required()
def get_orders():
    user_id = get_jwt_identity()
    user_role = run_query(f"select role from users where id = '{user_id}'")[0]['role']

    if user_role != "seller":
        return {'message': "Not Allowed"}, 401

    query = f"""select o.id, u.name as user_name, u.id as user_id, u.email as user_email, o.total_price as total, o.created_at
                from orders o join users u on o.buyer_id = u.id"""

    result = run_query(query)

    return {"data": result}, 200