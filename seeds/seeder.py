from flask_seeder import Seeder
from faker import Faker
from PIL import Image
from sqlalchemy import text, create_engine
import hashlib
import random
import string
import uuid
import os
import openai
import urllib.request
import sys

fake = Faker()


# All seeders inherit from Seeder
class DbSeeder(Seeder):

  # run() will be called by Flask-Seeder
  def run(self):
    engine_uri = "postgresql+psycopg2://{}:{}@{}:{}/{}".format(
        os.environ["POSTGRES_USER"],
        os.environ["POSTGRES_PASSWORD"],
        os.environ["POSTGRES_HOST"],
        os.environ["POSTGRES_PORT"],
        os.environ["POSTGRES_DB"],
    )

    engine = create_engine(engine_uri, future=True)

    with engine.connect() as conn:
        query = f"""
            delete from orders_cart;
            delete from seller_revenue;
            delete from product_size;
            delete from user_balance;
            delete from cart;
            delete from orders;
            delete from shipping_methods;
            delete from size;
            delete from users;
            delete from shipping_address;
            delete from product_images;
            delete from products;
            delete from categories;
            delete from images
        """
        conn.execute(text(query))
        conn.commit()

        # shipping_address
        shipping_address_id = []
        for i in range(5):
            id = uuid.uuid4()
            shipping_address_id.append(str(id))
            query = f"""
                insert into shipping_address values
                ('{id}', '{''.join(random.choices(['Rumah', 'Kantor', 'Kos']))}', '{fake.phone_number()}', '{fake.address()}', '{fake.city()}')
            """
            conn.execute(text(query))

        # users
        admin_id = '1'
        conn.execute(text(f"insert into users values ('{admin_id}', 'admin', 'admin@admin.com', '{fake.phone_number()}', '{hashlib.md5('password'.encode('utf8')).hexdigest()}', null, 'seller')"))

        user_id = []
        for i in range(0, 5):
            id = uuid.uuid4()
            user_id.append(str(id))
            query = f"""
                insert into users values
                ('{id}', '{fake.name()}', '{fake.email()}', '{fake.phone_number()}', '{hashlib.md5('password'.encode('utf8')).hexdigest()}', '{random.choices(shipping_address_id)[0]}', 'buyer')
            """
            conn.execute(text(query))

        # user balance
        for id in user_id:
            query = f"""
                insert into user_balance values
                ('{id}', {fake.random_int(min=100000, max=10000000)})
            """
            conn.execute(text(query))

        # seller_revenue
        conn.execute(text(f"insert into seller_revenue values ('{admin_id}', {fake.random_int(min=1000000, max=20000000)})"))

        # categories
        categories_name = [
            'Shirt',
            'Shorts', 
            'Hat',
            'Dress',
            'Skirt',
            'Shoes'
        ]
        categories_id = []
        for category_name in categories_name:
            id = uuid.uuid4()
            categories_id.append(str(id))
            query = f"""
                insert into categories values 
                ('{id}', '{category_name}', {fake.boolean()})
            """
            conn.execute(text(query))

        # products
        products = []

        index = 0
        for category in categories_name:
            for i in range(3):
                id = uuid.uuid4()
                color = fake.safe_color_name().capitalize()
                query = f"""
                    insert into products values 
                    ('{id}', '{color + ' ' + category}', '{color + ' ' + category}', '{random.choices(['new', 'used'])[0]}', {fake.random_int(min=100000, max=1000000, step=50000)}, {fake.boolean()}, '{categories_id[index]}')
                """
                products.append({"id": str(id), 'product_name': color + ' ' + category})
                conn.execute(text(query))
            
            index += 1

        # images
        # def run_query(query, commit: bool = False):
        #     """Runs a query against the given SQLite database.

        #     Args:
        #         commit: if True, commit any data-modification query (INSERT, UPDATE, DELETE)
        #     """
        #     # engine = create_engine()
        #     if isinstance(query, str):
        #         query = text(query)

        #     with engine.connect() as conn:
        #         if commit:
        #             conn.execute(query)
        #             conn.commit()
        #             conn.close()
        #         else:
        #             return [dict(row) for row in conn.execute(query)]

        # products = run_query(f"select id, product_name from products")
        # print(products)

        for product in products:
            response = openai.Image.create(
                prompt=product['product_name'],
                n=fake.random_int(min=1, max=3),
                size="1024x1024"
            )
            for resp in response['data']:
                image_url = resp['url']
                local_filename, headers = urllib.request.urlretrieve(image_url)


                file_name = ''.join(random.choices(string.ascii_lowercase +
                             string.digits, k=20)) + '.jpg'
                image = Image.open(local_filename)
                image.save(f'app/static/{file_name}')

                id = uuid.uuid4()
                conn.execute(text(f"insert into images values ('{id}', '{file_name}', '/image/{file_name}')"))
                conn.execute(text(f"insert into product_images values ('{product['id']}', '{id}')"))
        # product_images

        # shipping_methods
        conn.execute(text(f"insert into shipping_methods values ('{uuid.uuid4()}', 'regular')"))
        conn.execute(text(f"insert into shipping_methods values ('{uuid.uuid4()}', 'next day')"))

        # size
        size_id = []
        size = ['XS', 'S', 'M', 'L', 'XL', 'XL']

        for size in size:
            id = uuid.uuid4()
            size_id.append(str(id))
            query = f"""
                insert into size values ('{id}', '{size}');
            """
            conn.execute(text(query))

        # product_size
        for product_id in products:
            for this_size_id in size_id:
                conn.execute(text(f"insert into product_size values ('{product_id['id']}', '{this_size_id}')"))

        conn.commit()
        conn.close()