from flask import request, Blueprint
from utils import run_query
from flask_jwt_extended import jwt_required, get_jwt_identity
from cart.shipping_price import get_shipping_price
from datetime import datetime
import uuid

order_bp = Blueprint("order", __name__, url_prefix="/order")

@order_bp.route('', methods=['POST'])
@jwt_required()
def create_order():
    user_id = get_jwt_identity()
    body = request.json
    shipping_method = body['shipping_method']
    shipping_address = body['shipping_address']

    price = get_shipping_price()
    subtotal = price[0]['total_price']
    total_price = subtotal

    # masi bingung
    if shipping_method == "regular":
        total_price += price[0]['data'][0]['price']
    elif shipping_method == "next day":
        total_price += price[0]['data'][1]['price']

    user_balance = run_query(f"select balance from user_balance where user_id = '{user_id}'")[0]['balance']

    if user_balance < total_price:
        return {"error": "Not sufficient balances"}, 401

    shipping_address_id = run_query(f"""select * 
                                        from shipping_address 
                                        where address_name = '{shipping_address['name']}' and
                                            phone_number = '{shipping_address['phone_number']}' and
                                            address = '{shipping_address['address']}' and
                                            city = '{shipping_address['city']}'""")[0]['id']

    shipping_method_id = run_query(f"select id from shipping_methods where name = '{shipping_method}'")[0]['id']
    

    if shipping_address_id and shipping_method_id:
        cart_id = run_query(f"select id from cart where buyer_id = '{user_id}' and is_deleted = false")
        order_id = uuid.uuid4()

        query = f"""
            insert into orders (id, total_price, buyer_id, shipping_method_id, shipping_address_id, created_at)
            values ('{order_id}', {total_price}, '{user_id}', '{shipping_method_id}', '{shipping_address_id}', '{datetime.now()}')
        """

        run_query(query, True)

        for item in cart_id:
            run_query(f"insert into orders_cart values ('{order_id}', '{item['id']}')", True)

        run_query(f"update cart set is_deleted = true where buyer_id = '{user_id}'", True)

        run_query(f"update user_balance set balance = {user_balance - total_price} where user_id = '{user_id}'", True)

        run_query(f"update seller_revenue set revenue = revenue + {total_price} where user_id = '1'", True)
        return {"message": "Order success"}, 200
    else:
        return {"message": "Order failed"}, 401
