from flask import request,Blueprint
from utils import run_query, prepare_response

home_bp = Blueprint("home", __name__, url_prefix="/home")

@home_bp.route('/banner', methods=['GET'])
def get_banner():
    # query = """select b.id, b.title, i.path as image 
    #             from banner b join images i on b.image_id = i.id"""

    query = """select distinct on (p.category_id) p.id, p.product_name as title, i.path as image
                from products p 
                    join product_images pi on p.id = pi.product_id
                    join images i on pi.image_id = i.id
                    join categories c on p.category_id = c.id
                where p.is_available = true and c.is_available = true
                limit 5"""

    resp = run_query(query)
    return prepare_response({'data': resp}, 200)

@home_bp.route('/category', methods=['GET'])
def get_category():
    query = """select c.id, c.title, i.path as image 
                from categories c 
                    join (select distinct on (category_id) * 
                            from products join product_images pi on products.id = pi.product_id)
                        as cp on c.id = cp.category_id 
                    join images i on cp.image_id = i.id
                where c.is_available = true"""

    resp = run_query(query)
    return prepare_response({'data': resp}, 200)