from flask import request,Blueprint, send_from_directory
from utils import run_query, prepare_response

image_bp = Blueprint('image', __name__, url_prefix='/image')

@image_bp.route('/<path:image_name>', methods=['GET'])
def get_image(image_name):
    return send_from_directory('./static', image_name)