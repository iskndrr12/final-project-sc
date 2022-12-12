import re
import uuid
import hashlib
from flask import request,Blueprint
from utils import run_query


register_bp = Blueprint("sign-up", __name__, url_prefix="/sign-up")
@register_bp.route("", methods=["POST"])
def sign_up():
    # IMPLEMENT THIS
    body = request.json
    name = body['name']
    email= body['email']
    phone_number = body['phone_number']
    password = body['password']
    id_uuid_user = uuid.uuid4()

    if len(password) < 8:
        return  {"error": "Password must contain at least 8 characters"}, 400
    elif re.search('[a-z]', password) is None:
        return {"error": "Password must contain a lowercase letter"}, 400
    elif re.search('[A-Z]', password) is None:
        return {"error": "Password must contain an uppercase letter"}, 400
    elif re.search('[0-9]', password) is None:
        return {"error": "Password must contain a number"}, 400
    elif re.search('[!@#$%&()\-_[\]{};:"./<>?]', password) is None:
        return {"error": "Password must contain a special character"}, 400
    elif ({"email": email}) in run_query("SELECT email FROM users"):
        return {"error": f"email {email} already exists"}, 409
    elif ({"phone_number": phone_number}) in run_query("SELECT phone_number FROM users"):
        return {"error": f"phone number {phone_number} already exists"}, 409
    
    password = hashlib.md5(password.encode('utf8')).hexdigest()

    run_query(f'''INSERT INTO users (id, name, email, phone_number, password, role)
                VALUES('{id_uuid_user}', '{name}', '{email}','{phone_number}', '{password}', 'buyer')''', commit=True)
    run_query(f'''INSERT INTO User_balance (user_id, balance)
                VALUES('{id_uuid_user}', 0 )''', commit=True)
    return {"message": "User created successfully"}, 201
    