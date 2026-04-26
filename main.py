from flask import Flask
from config import Config
from models import db, login_manager
from flask_login import LoginManager
import os
from datetime import timedelta

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице'
    login_manager.login_message_category = 'info'

    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.wish import wish_bp
    from routes.feed import feed_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(wish_bp)
    app.register_blueprint(feed_bp)

    @app.template_filter('utc5')
    def utc5_filter(value):
        if value is None:
            return None
        return value + timedelta(hours=5)

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=8080)
