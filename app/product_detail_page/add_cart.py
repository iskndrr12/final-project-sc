from flask import request,Blueprint
from utils import run_query
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import uuid

add_cart_bp = Blueprint("cart", __name__, url_prefix="/cart")
@add_cart_bp.route("", methods= ['POST'])
@jwt_required()
def add_cart():
    body = request.json
    id_item = body['id']
    quantity = body ['quantity']
    size = body ['size']
    uuid_cart = uuid.uuid4()
    # uuid_size = uuid.uuid4()
    token = request.headers.get('token')
    token = get_jwt_identity() #identifikasi token berdasarkan id 
    
    buyer_id = run_query(f'''SELECT id FROM users
                         WHERE id = '{token}' AND role = 'buyer'
                          ''')
    updateQuantity = run_query(f"""SELECT cart.product_id,size_id
                     FROM cart 
                     INNER JOIN size
                     ON cart.size_id = size.id
                     WHERE cart.buyer_id = '{token}' AND cart.product_id = '{id_item}' AND size.size = '{size}' and cart.is_deleted = false
                     """)
    # size_id_cart = run_query(f""" SELECT cart.size_id FROM cart
    #                   INNER JOIN size
    #                   ON cart.size_id = size.id
    #                   WHERE size.size = '{size}'
    #                   AND cart.product_id = '{id_item}' AND cart.buyer_id = '{token}'  """)
    # if size_id_cart:
    #     size_id_cart = size_id_cart[0]['size_id']
    
    size_id_cart = run_query(f"""select id from size where size = '{size}'""")[0]['id']
        
    quantity_cart = run_query(f'''SELECT (cart.quantity + {quantity}) as quantity, created_at FROM cart
                              WHERE cart.product_id = '{id_item}' AND 
                              cart.size_id = '{size_id_cart}' AND cart.buyer_id = '{token}'
                              order by created_at desc
                              ''')
 
    if updateQuantity:
        quantity_cart = quantity_cart[0]['quantity']
        created_at = quantity_cart[0]['created_at']
        run_query(f"""UPDATE cart SET quantity = '{quantity_cart}'
                  WHERE cart.product_id= '{id_item}' AND 
                  cart.size_id = '{size_id_cart}' and cart.buyer_id = '{token}' and created_at = '{created_at}'""", True)
        
        return {"message": "item added to cart successfully"}, 201

    if buyer_id:
        buyer_id = buyer_id[0]['id']
        # run_query(f"""INSERT INTO size (id, size)
        #           VALUES('{uuid_size}', '{size}')
        #           """,True)
        run_query(f"""INSERT INTO cart(id,quantity,buyer_id, product_id, size_id, is_deleted, created_at)
                  VALUES('{uuid_cart}', '{quantity}', '{buyer_id}', '{id_item}', '{size_id_cart}', false, '{datetime.now()}')
                  """, True)
        # run_query(f"""INSERT INTO product_size(product_id,size_id)
        #           VALUES('{id_item}', '{size_id_cart}')
        #            ON conflict(product_id, size_id) do nothing
        #           """,True)
        return {"message": "item added to cart successfully"}, 201
    else:
        return{"message": "authorization error"}, 400
    
    