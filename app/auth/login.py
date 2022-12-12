from flask import request,Blueprint
from utils import run_query
from datetime import timedelta
from flask_jwt_extended import create_access_token
import hashlib


login_bp = Blueprint("sign-in", __name__, url_prefix="/sign-in")

@login_bp.route("", methods=["POST"])
def sign_in():
	body = request.json
	email = body ['email']
	password = body['password']
	password = hashlib.md5(password.encode('utf8')).hexdigest()
	
	id_user = run_query(f"SELECT id FROM users WHERE email = '{email}' ")
	if id_user:
		id_user = id_user[0]['id']
	else:
		return {'message': "Email or password is incorrect"}, 401

	
	token = create_access_token(identity=id_user) #indentifikasi token berdasarkan id

	if {"email": email} in run_query(f"SELECT email FROM users WHERE id = '{id_user}' and password != '{password}' "):
		return  {"message": "Email or password is incorrect"}, 401
	else: 
		user = run_query(f'''SELECT name, email, phone_number, role as type FROM users 
							WHERE users.id = '{id_user}' ''')
		return  {
			"user_information": user[0],
			"token": token,
			"message": "Login success"
		}, 200
        

        
   
   