from flask import request,Blueprint
from utils import run_query, prepare_response
from flask_jwt_extended import jwt_required, get_jwt_identity

category_bp = Blueprint("category", __name__, url_prefix="/categories")

@category_bp.route('', methods=['GET'])
@jwt_required(optional=True)
def get_category():
    user_id = get_jwt_identity()

    query = None
    if user_id:
        query = """select c.id, c.title
                from categories c
                """
    else:
        query = """select c.id, c.title
                    from categories c
                    where c.is_available = true"""

    resp = run_query(query)
    return prepare_response({'data': resp}, 200)