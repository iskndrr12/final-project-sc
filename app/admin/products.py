from flask import request, Blueprint
from utils import run_query
from flask_jwt_extended import get_jwt_identity, jwt_required
from products.products import products_bp
import base64
import string
import random
import uuid
from io import BytesIO
from PIL import Image
import sys

# products_bp = Blueprint('products', __name__, url_prefix='/products')

@products_bp.route('', methods=['POST'])
@jwt_required()
def create_product():
    user_id = get_jwt_identity()
    user_role = run_query(f"select role from users where id = '{user_id}'")[0]['role']

    if user_role != "seller":
        return {'message': "Not Allowed"}, 401

    body = request.json
    product_name = body['product_name']
    desc = body['description'] if 'description' in body else ""
    images = body['images']
    condition = body['condition']
    category = body['category']
    price = body['price']

    # check apakah unique
    is_not_unique = run_query(f"""select * from products 
                                where product_name = '{product_name}' and 
                                    category_id = '{category}' and 
                                    condition = '{condition}'""")

    if is_not_unique :
        return {'message': "Product is already exist"}, 400

    # store product
    id = uuid.uuid4()
    run_query(f"""insert into products 
                    (id, product_name, description, condition, category_id, price, is_available)
                    values ('{id}', '{product_name}', '{desc}', '{condition}', '{category}', {price}, true)""", True)

    # image handle
    if images:
        for image in images:
            base64_data = image.split(',')
            img_data = bytes(base64_data[1], encoding="ascii")
            file_name = ''.join(random.choices(string.ascii_lowercase +
                             string.digits, k=20)) + f".{base64_data[0].split('/')[1].split(';')[0]}"

            im = Image.open(BytesIO(base64.b64decode(img_data)))
            im.save('app/static/'+f'{file_name}')

            # store to db
            image_id = uuid.uuid4()
            run_query(f"""insert into images 
                            values ('{image_id}', '{file_name}', '/image/{file_name}')""", True)
            run_query(f"""insert into product_images
                            values ('{id}', '{image_id}')""", True)

    return {"message": "Product added"}, 201

@products_bp.route("/<path:product_id>", methods=['GET'])
@jwt_required()
def get_specific_product(product_id):
    user_id = get_jwt_identity()
    user_role = run_query(f"select role from users where id = '{user_id}'")[0]['role']

    if user_role != "seller":
        return {'message': "Not Allowed"}, 401

    query = f"""select p.product_name as title, p.description as product_detail, p.condition, p.category_id, p.price
                from products p 
                    join product_images pi on p.id = pi.product_id
                where product_id = '{product_id}'"""

    query_images = f"""select i.path
                        from images i
                            join product_images pi on i.id = pi.image_id
                        where pi.product_id = '{product_id}'"""

    image_result = []
    for path in run_query(query_images):
        image_result.append(path['path'])

    result = run_query(query)[0]
    result['images_url'] = image_result

    return {"data": result}, 200

@products_bp.route('', methods=['PUT'])
@jwt_required()
def update_product():
    user_id = get_jwt_identity()
    user_role = run_query(f"select role from users where id = '{user_id}'")[0]['role']

    if user_role != "seller":
        return {'message': "Not Allowed"}, 401

    body = request.json
    product_id = body['product_id']
    product_name = body['product_name']
    desc = body['description'] if 'description' in body else ""
    images = body['images']
    condition = body['condition']
    category = body['category']
    price = body['price']

    # check apakah unique
    is_not_unique = run_query(f"""select * from products 
                                    where product_name = '{product_name}' and 
                                        category_id = '{category}' and 
                                        condition = '{condition}'
                                    union 
                                    select * from products 
                                    where id = '{product_id}'""")

    if len(is_not_unique) > 1 :
        return {'message': "Product is already exist"}, 400

    # update product
    run_query(f"""update products 
                    set 
                        product_name = '{product_name}',
                        description = '{desc}', 
                        condition = '{condition}',
                        category_id = '{category}',
                        price = {price}
                    where id = '{product_id}'""", True)

    # image handle
    if images:
        for image in images:
            if image.find('base64') == -1:
                print(image.find('base64'), file=sys.stderr)
                continue

            base64_data = image.split(',')
            img_data = bytes(base64_data[1], encoding="ascii")
            file_name = ''.join(random.choices(string.ascii_lowercase +
                             string.digits, k=20)) + f".{base64_data[0].split('/')[1].split(';')[0]}"

            im = Image.open(BytesIO(base64.b64decode(img_data)))
            im.save('app/static/'+f'{file_name}')

            # store to db
            image_id = uuid.uuid4()
            run_query(f"""insert into images 
                            values ('{image_id}', '{file_name}', '/image/{file_name}')""", True)
            run_query(f"""insert into product_images
                            values ('{product_id}', '{image_id}')""", True)

    return {"message": "Product updated"}, 201

@products_bp.route('/<path:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    user_id = get_jwt_identity()
    user_role = run_query(f"select role from users where id = '{user_id}'")[0]['role']

    if user_role != "seller":
        return {'message': "Not Allowed"}, 401

    run_query(f"""update products set is_available = false
                    where id = '{product_id}' """, True)

    return {'message': 'Product deleted'}, 200