from flask import request,jsonify,Blueprint
from utils import run_query
from flask_jwt_extended import jwt_required, get_jwt_identity
from profile_page.user_details import user_bp

@user_bp.route("balance", methods = ['POST'])
@jwt_required()
def balance():
    body = request.json
    amount = body['amount']
    amount = int(amount)
    # token = request.headers.get('token')
    user_id = get_jwt_identity()
    
    # user_id_balance = run_query(f"SELECT user_id FROM user_balance WHERE user_id = '{token}' ")
    # if user_id_balance:
    #     user_id_balance = user_id_balance[0]['user_id']
    
    top_up_amount = run_query(f'''SELECT SUM(balance + {amount}) as amount FROM user_balance 
                              WHERE user_id = '{user_id}' ''')
    top_up_amount = int(top_up_amount[0]['amount'])
    
    if not amount:
        return jsonify ({"message": "please specify amount"}), 401
    elif amount < 1:
        return jsonify({"message": "Please specify a positive amount"}), 400
    elif {"user_id": user_id} in run_query ("SELECT user_id FROM user_balance"):
        run_query(f'''UPDATE user_balance SET balance = {top_up_amount} WHERE user_id = '{user_id}' 
                  ''' , commit=True)
        return jsonify ({"message": "Top up success"}),200
    else:
        return jsonify({"message": "Top up failed"}), 400

@user_bp.route("balance", methods = ['GET'])
@jwt_required()
def get_balance():
    # amount = request.args.get('amount')
#    token = request.headers.get('token')
    id_user = get_jwt_identity()

    # user_id_balance = run_query(f"SELECT user_id FROM user_balance WHERE user_id = '{token}' ")
    # if user_id_balance:
    #     user_id_balance = user_id_balance[0]['user_id']
    
    if {"user_id": id_user} in run_query ("SELECT user_id FROM user_balance"):
        balance = run_query(f"SELECT balance FROM user_balance WHERE user_id = '{id_user}' ")
        return jsonify ({"data": balance[0]}), 200
    else:
        return jsonify ({"message": "not found balance"}), 400
   
