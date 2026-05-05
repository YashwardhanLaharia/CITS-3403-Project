from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)


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
def dashboard():
    return render_template('dashboard.html')


@main_bp.route('/profile')
def profile():
    return render_template('profile.html')


@main_bp.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
