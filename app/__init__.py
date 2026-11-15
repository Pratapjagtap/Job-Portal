import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash

from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Global Context Processor to guarantee profile_user is available in all views
    @app.context_processor
    def inject_global_vars():
        user = current_user if current_user.is_authenticated else None
        return dict(profile_user=user)

    from app.routes.auth import auth_bp
    from app.routes.jobs import jobs_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(jobs_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')

    with app.app_context():
        db.create_all()
        _init_db(app)

    return app


def _init_db(app):
    from app.models import User, Job
    # Auto-seed if empty
    if Job.query.count() == 0 or User.query.filter_by(username='elena').first() is None:
        try:
            from seed_data import seed
            seed(app)
        except Exception as e:
            print("Auto-seed notice:", e)

    demo_user = User.query.filter_by(username='elena', full_name='Elena Vance').first()
    if demo_user:
        demo_user.full_name = ''
        db.session.commit()


def role_required(*roles):
    from functools import wraps
    from flask import abort

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
