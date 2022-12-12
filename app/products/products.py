from flask import request,Blueprint
from utils import run_query, prepare_response
from flask_jwt_extended import jwt_required, get_jwt_identity
import sys

products_bp = Blueprint("products", __name__, url_prefix="/products")

@products_bp.route('', methods=['GET'])
@jwt_required(optional=True)
def get_product_list():
    args = request.args

    result = None

    is_admin = get_jwt_identity()
    if is_admin:
        query = f"""select p.id, i.path as image, p.product_name as title, p.price
                        from products p 
                            join (select distinct on (product_id) * from product_images) as pi on p.id = pi.product_id
                            join images i on pi.image_id = i.id
            """
        result = run_query(query)

    else:
        if len(args) == 3:
            query = f"""select p.id, i.path as image, p.product_name as title, p.price
                        from products p 
                            join (select distinct on (product_id) * from product_images) as pi on p.id = pi.product_id
                            join images i on pi.image_id = i.id
                            join categories c on p.category_id = c.id
                        where p.is_available = true and
                        c.is_available = true
            """
            result = run_query(query)

        if args.get('category') and args.get('price') and args.get('condition'):
            price = args.get('price').split(sep=',')
            category = args.get('category')
            if args.get('category').find(','):
                category = args.get('category').split(',')
                query = ''
                for category_id in category:
                    query += f"""select p.id, i.path as image, p.product_name as title, p.price
                        from products p 
                            join (select distinct on (product_id) * from product_images) as pi on p.id = pi.product_id
                            join images i on pi.image_id = i.id
                            join categories c on p.category_id = c.id
                        where p.category_id = '{category_id}' and
                            p.price between {price[0]} and {price[1]} and
                            p.condition = '{args.get('condition')}' and
                            p.is_available = true and
                            c.is_available = true
                        union """
                query = query.strip('union ')
                # print(query, file=sys.stderr)
                result = run_query(query)
            else:
                query = f"""select p.id, i.path as image, p.product_name as title, p.price
                            from products p 
                                join (select distinct on (product_id) * from product_images) as pi on p.id = pi.product_id
                                join images i on pi.image_id = i.id
                                join categories c on p.category_id = c.id
                            where p.category_id = '{str(args.get('category'))}' and
                                p.price between {price[0]} and {price[1]} and
                                p.condition = '{args.get('condition')}' and
                                p.is_available = true and
                                c.is_available = true"""
                result = run_query(query)
        elif args.get('category') and args.get('price') == None and args.get('condition') == None:
            category = args.get('category')
            if args.get('category').find(','):
                category = args.get('category').split(',')
                query = ''
                for category_id in category:
                    query += f"""select p.id, i.path as image, p.product_name as title, p.price
                                from products p 
                                    join (select distinct on (product_id) * from product_images) as pi on p.id = pi.product_id
                                    join images i on pi.image_id = i.id
                                    join categories c on p.category_id = c.id
                                where p.category_id = '{category_id}' and
                                p.is_available = true and
                                c.is_available = true
                                union """
                query = query.strip('union ')
                # print(query, file=sys.stderr)
                result = run_query(query)
            else:
                query = f"""select p.id, i.path as image, p.product_name as title, p.price
                                from products p 
                                    join (select distinct on (product_id) * from product_images) as pi on p.id = pi.product_id
                                    join images i on pi.image_id = i.id
                                    join categories c on p.category_id = c.id
                                where p.category_id = '{category_id}' and
                                p.is_available = true and
                                c.is_available = true"""

                result = run_query(query)

        elif args.get('category') == None and args.get('price') and args.get('condition') == None:
            price = args.get('price').split(sep=',')
            query = f"""select p.id, i.path as image, p.product_name as title, p.price
                        from products p 
                            join (select distinct on (product_id) * from product_images) as pi on p.id = pi.product_id
                            join images i on pi.image_id = i.id
                            join categories c on p.category_id = c.id
                        where p.price between {price[0]} and {price[1]} and
                        p.is_available = true and
                        c.is_available = true
            """
            result = run_query(query)
        elif args.get('category') == None and args.get('price') == None and args.get('condition'):
            query = f"""select p.id, i.path as image, p.product_name as title, p.price
                        from products p 
                            join (select distinct on (product_id) * from product_images) as pi on p.id = pi.product_id
                            join images i on pi.image_id = i.id
                            join categories c on p.category_id = c.id
                        where p.condition = '{args.get('condition')}' and
                        p.is_available = true and
                        c.is_available = true
            """
            result = run_query(query)
        elif args.get('category') and args.get('price') == None and args.get('condition'):
            category = args.get('category')
            if args.get('category').find(','):
                category = args.get('category').split(',')
                query = ''
                for category_id in category:
                    query += f"""select p.id, i.path as image, p.product_name as title, p.price
                        from products p 
                            join (select distinct on (product_id) * from product_images) as pi on p.id = pi.product_id
                            join images i on pi.image_id = i.id
                            join categories c on p.category_id = c.id
                        where p.condition = '{args.get('condition')}' and
                            p.category_id = '{category_id}' and
                            p.is_available = true and
                            c.is_available = true
                        union """
                query = query.strip('union ')
                # print(query, file=sys.stderr)
                result = run_query(query)
            else:
                query = f"""select p.id, i.path as image, p.product_name as title, p.price
                            from products p 
                                join (select distinct on (product_id) * from product_images) as pi on p.id = pi.product_id
                                join images i on pi.image_id = i.id
                                join categories c on p.category_id = c.id
                            where p.condition = '{args.get('condition')}' and
                                p.category_id = '{args.get('category')}' and
                                p.is_available = true and
                                c.is_available = true"""
                result = run_query(query)
        elif args.get('category') == None and args.get('price') and args.get('condition'):
            price = args.get('price').split(sep=',')
            query = f"""select p.id, i.path as image, p.product_name as title, p.price
                        from products p 
                            join (select distinct on (product_id) * from product_images) as pi on p.id = pi.product_id
                            join images i on pi.image_id = i.id
                            join categories c on p.category_id = c.id
                        where p.condition = '{args.get('condition')}' and
                            p.price between {price[0]} and {price[1]} and
                            p.is_available = true and
                            c.is_available = true
            """
            result = run_query(query)
        elif args.get('category') and args.get('price') and args.get('condition') == None:
            price = args.get('price').split(sep=',')
            category = args.get('category')
            if args.get('category').find(','):
                category = args.get('category').split(',')
                query = ''
                for category_id in category:
                    query += f"""select p.id, i.path as image, p.product_name as title, p.price
                        from products p 
                            join (select distinct on (product_id) * from product_images) as pi on p.id = pi.product_id
                            join images i on pi.image_id = i.id
                            join categories c on p.category_id = c.id
                        where p.category_id = '{category_id}' and
                            p.price between {price[0]} and {price[1]} and
                            p.is_available = true and
                            c.is_available = true
                            union """
                query = query.strip('union ')
                # print(query, file=sys.stderr)
                result = run_query(query)
            else:
                query = f"""select p.id, i.path as image, p.product_name as title, p.price
                            from products p 
                                join (select distinct on (product_id) * from product_images) as pi on p.id = pi.product_id
                                join images i on pi.image_id = i.id
                                join categories c on p.category_id = c.id
                            where p.category_id = '{args.get('category')}' and
                                p.price between {price[0]} and {price[1]} and
                                p.is_available = true and
                                c.is_available = true"""
                result = run_query(query)

        def price_sort(obj):
            return obj['price']
            
        if args.get('sort_by') == 'Price a_z':
            result.sort(key=price_sort)
        elif args.get('sort_by') == 'Price z_a':
            result.sort(reverse=True, key=price_sort)

    return prepare_response({'data': result, 'total_rows': len(result)}, 200)