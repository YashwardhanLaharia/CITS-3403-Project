import os
from datetime import timedelta
from flask import Flask
from flask_login import LoginManager
from models import db, User

login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder='frontendCode', static_folder='frontendCode')
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=14)
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    with app.app_context():
        db.create_all()
    
    from routes import auth_bp, main_bp
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(main_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)