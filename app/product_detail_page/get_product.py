from flask import request,Blueprint
from utils import run_query
from products.products import products_bp
from flask_jwt_extended import jwt_required, get_jwt_identity

@products_bp.route("/<path:id>", methods= ['GET'])
@jwt_required(optional=True)
def get_products_details(id):
    user_id = get_jwt_identity()

    if user_id:
        user_role = run_query(f"select role from users where id = '{user_id}'")[0]['role']

        if user_role != "seller":
            return {'message': "Not Allowed"}, 401

        query = f"""select p.product_name as title, p.description as product_detail, p.condition, p.category_id, p.price
                    from products p 
                        join product_images pi on p.id = pi.product_id
                    where product_id = '{id}'"""

        query_images = f"""select i.path
                            from images i
                                join product_images pi on i.id = pi.image_id
                            where pi.product_id = '{id}'"""

        image_result = []
        for path in run_query(query_images):
            image_result.append(path['path'])

        result = run_query(query)[0]
        result['images_url'] = image_result

        return {"data": result}, 200
    
    else:
        if {"id": id} in run_query(f"SELECT id FROM products where id = '{id}' "):
            query = f"""SELECT products.id, products.product_name as title,
                        products.description as product_detail,
                        products.price, products.category_id,
                        categories.title as category_name
                    FROM products
                    JOIN categories ON products.category_id = categories.id
                    WHERE products.id = '{id}'
                    """
            query_image = f"""select i.path 
                                from images i
                                join product_images pi on i.id = pi.image_id
                                join products p on pi.product_id = p.id
                                where p.id = '{id}'"""
            query_size = f"""select s.size from size s
                                join product_size ps on s.id = ps.size_id
                                join products p on ps.product_id = p.id
                                where p.id = '{id}'"""

            result = run_query(query)[0]
            
            result['images_url'] = []
            for image in run_query(query_image):
                result['images_url'].append(image['path'])

            result['size'] = []
            for size in run_query(query_size):
                result['size'].append(size['size'])

            return {"data": result}, 200
        else:
            return {"message": "product is not found"}
        # return f"ini adalah ini dari {id}"

    

