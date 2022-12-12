from sqlalchemy import (
    Column, 
    MetaData, 
    String, 
    Table, 
    Integer, 
    ForeignKey, 
    Boolean,
    DateTime,
    UniqueConstraint,
    PrimaryKeyConstraint
)
from sqlalchemy.exc import IntegrityError
from utils import get_engine
from flask import Flask
from datetime import timedelta
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_seeder import FlaskSeeder
import os
import openai

from auth.register import register_bp
from auth.login import login_bp
from home.home import home_bp
from products.category import category_bp
from products.products import products_bp
from universal.image import image_bp
from profile_page.user_details import user_bp
from profile_page.shipping_address import user_bp
from profile_page.balance import user_bp
from product_detail_page.add_cart import add_cart_bp
from product_detail_page.get_product import products_bp
from admin.sales import sales_bp
from admin.products import products_bp
from admin.categories import category_bp
from admin.orders import orders_bp
from cart.cart import add_cart_bp
from cart.shipping_price import shipping_price_bp
from cart.order import order_bp
from profile_page.user_orders import user_bp



def create_app():
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = "secret"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=10)
    app.config["JWT_HEADER_NAME"] = "Authentication"
    app.config["JWT_HEADER_TYPE"] = ""
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://{}:{}@{}:{}/{}".format(
        os.environ["POSTGRES_USER"],
        os.environ["POSTGRES_PASSWORD"],
        os.environ["POSTGRES_HOST"],
        os.environ["POSTGRES_PORT"],
        os.environ["POSTGRES_DB"],
    )
    openai.api_key = os.getenv("OPENAI_API_KEY")
    jwt = JWTManager(app)
    CORS(app)

    db = SQLAlchemy(app)
    migrate = Migrate(app, db)

    seeder = FlaskSeeder()
    seeder.init_app(app, db)
   
    engine = get_engine()
    meta = MetaData()
    Table(
        "users",
        meta,
        Column("id", String, primary_key=True),
        Column("name", String, nullable=False),
        Column("email", String, nullable=False),
        Column("phone_number", String, nullable=False),
        Column("password", String, nullable=False),
        Column("shipping_address_id", ForeignKey('shipping_address.id'), nullable=True),
        Column("role", String, nullable=False),
    )
    
    Table(
        "shipping_address",
        meta,
        Column("id", String, primary_key=True),
        Column("address_name", String, nullable=False),
        Column("phone_number", String, nullable=False),
        Column("address", String, nullable=False),
        Column("city", String, nullable=False),
    )
    
    Table(
        "user_balance",
        meta,
        # waktu register user baru & type/role buyer, insert juga di tabel ini dgn balance 0
        Column("user_id", ForeignKey('users.id'), nullable=False),
        Column("balance", Integer, nullable=False),
        PrimaryKeyConstraint('user_id', 'balance')
    )
    
    Table(
        "seller_revenue",
        meta,
        # waktu register user baru & type/role seller, insert juga di tabel ini dgn revenue 0
        Column("user_id", ForeignKey('users.id'), nullable=False),
        Column("revenue", Integer, nullable=False),
        PrimaryKeyConstraint('user_id', 'revenue')
    )
    
    Table(
        "cart",
        meta,
        Column("id", String, primary_key=True),
        Column("quantity", Integer, nullable=False),
        Column("buyer_id", ForeignKey('users.id'), nullable=False),
        Column("product_id", ForeignKey('products.id'), nullable=False),
        Column("size_id", ForeignKey('size.id'), nullable=False),
        Column("is_deleted", Boolean, nullable=False, default=False),
        Column("created_at", DateTime, nullable=False),
        UniqueConstraint("product_id", "size_id", "created_at")
    )
    
    Table(
        "categories",
        meta,
        Column("id", String, primary_key=True),
        Column("title", String, nullable=False, unique=True),
        Column("is_available", Boolean, nullable=False),
    )
    
    Table(
        "products",
        meta,
        Column("id", String, primary_key=True),
        Column("product_name", String, nullable=False),
        Column("description", String, nullable=False),
        Column("condition", String, nullable=False),
        Column("price", Integer, nullable=False),
        Column("is_available", Boolean, nullable=False), #available ato tidak
        Column("category_id", ForeignKey('categories.id'), nullable=False),
        UniqueConstraint("product_name", "condition", "category_id")
    )
    
    Table(
        "orders",
        meta,
        Column("id", String, primary_key=True),
        Column("total_price", Integer, nullable=False),
        Column("buyer_id", ForeignKey('users.id'), nullable=False),
        Column("shipping_method_id", ForeignKey('shipping_methods.id'), nullable=False),
        Column("shipping_address_id", ForeignKey('shipping_address.id'), nullable=False),
        Column("created_at", DateTime, nullable=False),
    )

    Table(
        "shipping_methods",
        meta,
        Column('id', String, primary_key=True),
        Column('name', String),
    )
    
    Table(
        "images",
        meta,
        Column('id', String, primary_key=True),
        Column('image_name', String, nullable=False),
        Column('path', String, nullable=False),
    )
    
    Table(
        "size",
        meta,
        Column('id', String, primary_key=True),
        Column('size', String, nullable=False),
    )
    
    Table(
        "product_size",
        meta,
        Column('product_id', ForeignKey('products.id'), nullable=False),
        Column('size_id', ForeignKey('size.id'), nullable=False),
        PrimaryKeyConstraint('product_id', 'size_id')
    )
    
    Table(
        "product_images",
        meta,
        Column('product_id', ForeignKey('products.id'), nullable=False),
        Column('image_id', ForeignKey('images.id'), nullable=False),
        PrimaryKeyConstraint('product_id', 'image_id')
    )

    Table(
        "orders_cart",
        meta,
        Column('order_id', ForeignKey("orders.id"), nullable=False),
        Column('cart_id', ForeignKey("cart.id"), nullable=False),
        PrimaryKeyConstraint('order_id', 'cart_id')
    )

    
    meta.create_all(engine)

    blueprints = [
        register_bp,
        login_bp, 
        home_bp, 
        category_bp, 
        products_bp, 
        image_bp, 
        user_bp, 
        sales_bp, 
        add_cart_bp,
        shipping_price_bp,
        order_bp, 
        orders_bp
    ]

    for bp in blueprints:
        app.register_blueprint(bp)

    return app


app = create_app()

@app.route('/')
def index():
    return "Hello"

# if __name__ == "__main__":
#     app.run(debug=True, host = '0.0.0.0', port=5000)


app.run(host='0.0.0.0', port='5000')
