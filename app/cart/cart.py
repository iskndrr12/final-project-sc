from flask import request,Blueprint
from utils import run_query
from flask_jwt_extended import jwt_required, get_jwt_identity
from product_detail_page.add_cart import add_cart_bp
import uuid

@add_cart_bp.route('', methods=['GET'])
@jwt_required()
def get_user_cart():
    user_id = get_jwt_identity()

    query = f"""
        select distinct on (c.product_id, c.size_id) c.id, c.quantity, s.size, p.price, i.path as image, p.product_name as name
        from cart c
            join products p on c.product_id = p.id
            join product_images pi on p.id = pi.product_id
            join images i on pi.image_id = i.id
            join size s on c.size_id = s.id
        where c.buyer_id = '{user_id}' and c.is_deleted = false
    """

    result = run_query(query)

    for item in result:
        quantity = item['quantity']
        size = item['size']

        del item['quantity']
        del item['size']

        item['details'] = {"quantity": quantity, "size": size}

    return {"data": result}, 200

@add_cart_bp.route('<path:cart_id>', methods=['DELETE'])
@jwt_required()
def delete_cart(cart_id):
    user_id = get_jwt_identity()

    query = f"""
        delete from cart where id = '{cart_id}' and buyer_id = '{user_id}'
    """

    run_query(query, True)

    return {'message': 'Cart deleted'}, 200
