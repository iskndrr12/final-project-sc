from flask import request, Blueprint
from utils import run_query
from flask_jwt_extended import get_jwt_identity, jwt_required
from products.category import category_bp
import uuid

@category_bp.route('', methods=['POST'])
@jwt_required()
def create_category():
    user_id = get_jwt_identity()
    user_role = run_query(f"select role from users where id = '{user_id}'")[0]['role']

    if user_role != "seller":
        return {'message': "Not Allowed"}, 401

    body = request.json
    category_name = body['category_name']

    # check apakah unique
    is_not_unique = run_query(f"""select * from categories
                                    where title = '{category_name}'""")

    if is_not_unique:
        return {'message': "Category is already exist"}, 400

    # store category
    id = uuid.uuid4()
    query = f"""insert into categories 
                values ('{id}', '{category_name}', true)"""

    run_query(query, True)

    return {'message': "Category added"}, 201

@category_bp.route('/<path:category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    user_id = get_jwt_identity()
    user_role = run_query(f"select role from users where id = '{user_id}'")[0]['role']

    if user_role != "seller":
        return {'message': "Not Allowed"}, 401

    body = request.json
    category_name = body['category_name']

    # check apakah unique
    is_not_unique = run_query(f"""select * from categories
                                    where title = '{category_name}'
                                    union
                                    select * from categories 
                                    where id = '{category_id}'""")

    if len(is_not_unique) > 1:
        return {'message': "Category is already exist"}, 400

    run_query(f"""update categories
                    set title = '{category_name}'
                    where id = '{category_id}'""", True)

    return {"message": "Category updated"}, 201


@category_bp.route('/<path:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    user_id = get_jwt_identity()
    user_role = run_query(f"select role from users where id = '{user_id}'")[0]['role']

    if user_role != "seller":
        return {'message': "Not Allowed"}, 401

    run_query(f"""update categories
                    set is_available = false
                    where id = '{category_id}'""", True)

    return {"message": "Category deleted"}, 201