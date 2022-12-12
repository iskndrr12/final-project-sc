from flask import request, Blueprint
from utils import run_query
from flask_jwt_extended import jwt_required, get_jwt_identity
import uuid

shipping_price_bp = Blueprint("shipping_price", __name__, url_prefix="/shipping_price")

@shipping_price_bp.route('', methods=['GET'])
@jwt_required()
def get_shipping_price():
    user_id = get_jwt_identity()

    if not run_query(f"select * from cart where buyer_id = '{user_id}'"):
        return {"message": "Cart is empty"}, 200

    cart_query = f"""
        select sum(c.quantity * p.price) as total_price
        from cart c
            join products p on c.product_id = p.id
        where c.buyer_id = '{user_id}' and c.is_deleted = false
    """

    total_price = run_query(cart_query)[0]['total_price']

    regular_price = total_price * 15 / 100 if total_price < 200000 else total_price * 20 / 100
    nextday_price = total_price * 20 / 100 if total_price < 300000 else total_price * 25 / 100

    return {
        "data": [
            {
                "name": "regular",
                "price": regular_price
            },
            {
                "name": "next day",
                "price": nextday_price
            }
        ],
        "total_price": total_price
    }, 200


