from flask import Flask
from flask_login import LoginManager
from flask_ckeditor import CKEditor
from .config import Config
from .db import DB


login = LoginManager()
login.login_view = 'users.login'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    ckeditor = CKEditor(app)

    app.db = DB(app)
    login.init_app(app)

    from .index import bp as index_bp
    app.register_blueprint(index_bp)

    from .users import bp as user_bp
    app.register_blueprint(user_bp)

    from .inventory import bp as inventory_bp
    app.register_blueprint(inventory_bp)

    from .products import bp as products_bp
    app.register_blueprint(products_bp)

    from .reviews import bp as reviews_bp
    app.register_blueprint(reviews_bp)

    from .summary_rating import bp as summary_rating_bp
    app.register_blueprint(summary_rating_bp)
    
    from .carts import bp as cart_bp
    app.register_blueprint(cart_bp)

    from .purchases import bp as purchase_bp
    app.register_blueprint(purchase_bp)

    from .invhub import bp as invhub_bp
    app.register_blueprint(invhub_bp)

    from .balances import bp as balances_bp
    app.register_blueprint(balances_bp)

    from .myprofile import bp as myprofile_bp
    app.register_blueprint(myprofile_bp)

    return app
