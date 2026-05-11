from flask import Blueprint, render_template
from flask_login import login_required
from extensions import db, login_manager
from models import User

main_bp = Blueprint('main', __name__)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/login')
def login():
    return render_template('login.html')


@main_bp.route('/signup')
def signup():
    return render_template('signup.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@main_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@main_bp.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
