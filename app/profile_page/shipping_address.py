from flask import request,jsonify,Blueprint
from utils import run_query
from flask_jwt_extended import jwt_required, get_jwt_identity
import uuid
from profile_page.user_details import user_bp

@user_bp.route("/shipping_address", methods = ['POST'])
@jwt_required()
def Change_shipping_address():
    body = request.json
    Address_name = body['name']
    Phone_number = body['phone_number']
    Address = body['address']
    City = body['city'] 
    id_shiping_address = uuid.uuid4()
    id_user = get_jwt_identity()

    if ({"id": id_user}) in run_query ("SELECT id FROM users"):
        shipping_address_id = run_query(f"select shipping_address_id from users where id = '{id_user}'")[0]['shipping_address_id']
        if shipping_address_id:
            run_query(f'''UPDATE shipping_address SET address_name = '{Address_name}', phone_number = '{Phone_number}', address = '{Address}', city = '{City}' WHERE id = '{shipping_address_id}' 
                        ''',commit=True)
            return jsonify ({"message": "Shipping address updated successfully"}),201
        else :
            run_query(f'''INSERT INTO shipping_address(id, address_name, phone_number, address, city)
                        VALUES('{id_shiping_address}', '{Address_name}', '{Phone_number}', '{Address}', '{City}')
                    ''', commit=True)
            run_query(f"""update users set shipping_address_id = '{id_shiping_address}' where id = '{id_user}'""", True)
            return {"message": "Shipping address created successfully"}, 201
    else:
        return jsonify ({"message": "data is not change"}), 400
    
@user_bp.route("/shipping_address", methods = ['GET'])
@jwt_required()
def get_user_shiping_adress():
    token = get_jwt_identity()
    id_user_shipping = run_query(f'''SELECT shipping_address_id as id from users
                                    WHERE users.id = '{token}' ''')
    if id_user_shipping:
        id_user_shipping = id_user_shipping[0]['id']

    # query = f"""select sa.id, sa.name, sa.phone_number, sa.address, sa.city
    #             from users join shipping_address sa on users.shipping_address_id = sa.id
    #             where users.id = '{token}'"""
        
    
    if {"id": id_user_shipping} in run_query ("SELECT id FROM shipping_address"):
        data_shiping_address = run_query(f"SELECT id, address_name as name, phone_number, address, city FROM shipping_address WHERE id = '{id_user_shipping}' ")
        return jsonify ({"data": data_shiping_address[0]}), 200
    else:
        return jsonify ({"message": "data is not found"}), 400