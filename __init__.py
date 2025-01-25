from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from . import settings
db = SQLAlchemy()
upload_status = {}

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = settings.secret_key
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.sql_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle' : 280}
    app.config['UPLOAD_FOLDER'] = 'static/videos'

    from .models import User, Base

    db.init_app(app)
    with app.app_context():
        db.create_all()
        local_urls = Base.query.filter(Base.mainurl.like(f'{"/static/videos/"}%')).all() 
        for url in local_urls:
            upload_status[url.baseurl + '.mp4'] = 'uploaded'

    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
        

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))


    from .upload import upload
    app.register_blueprint(upload)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .view_pages import view_pages as view_pages_blueprint
    app.register_blueprint(view_pages_blueprint)

    from .view_videos import view_videos as view_videos_blueprint
    app.register_blueprint(view_videos_blueprint)
    return app

    from .payout import payout as payout_blueprint
    app.register_blueprint(payout_blueprint)