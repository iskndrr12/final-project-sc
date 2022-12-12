from flask import request, Blueprint
from utils import run_query
from flask_jwt_extended import jwt_required, get_jwt_identity
from profile_page.user_details import user_bp

@user_bp.route('/order', methods=['GET'])
@jwt_required()
def user_orders():
    user_id = get_jwt_identity()

    orders_query = f"""
        select o.id, o.created_at, sm.name as shipping_method, shipping_address_id
        from orders o
            join shipping_methods sm on o.shipping_method_id = sm.id
        where o.buyer_id = '{user_id}' 
    """

    orders = run_query(orders_query)

    for order in orders:
        order['products'] = []
        cart_id = run_query(f"""
            select cart_id from orders_cart where order_id = '{order['id']}'
        """)

        for cart_id in cart_id:
            query = f"""
                select distinct on (c.product_id, c.size_id) p.id, c.quantity, s.size, p.price, i.path as image, p.product_name as name
                from cart c
                    join products p on c.product_id = p.id
                    join product_images pi on p.id = pi.product_id
                    join images i on pi.image_id = i.id
                    join size s on c.size_id = s.id
                where c.id = '{cart_id['cart_id']}'
            """

            result = run_query(query)

            for item in result:
                quantity = item['quantity']
                size = item['size']

                del item['quantity']
                del item['size']

                item['details'] = {"quantity": quantity, "size": size}

            order['products'].append(result[0])
        
        shipping_address = run_query(f"select address_name as name, phone_number, address, city from shipping_address where id = '{order['shipping_address_id']}'")[0]
        del order['shipping_address_id']
        order['shipping_address'] = shipping_address

    return {"data": orders}, 200