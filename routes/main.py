from flask import send_from_directory, redirect
from flask_login import current_user, login_required
from routes import main_bp
import os

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontendCode')

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect('/index')
    return redirect('/login')

@main_bp.route('/login')
def login():
    return send_from_directory(FRONTEND_DIR, 'login.html')

@main_bp.route('/signup')
def signup():
    return send_from_directory(FRONTEND_DIR, 'signup.html')

@main_bp.route('/index')
@login_required
def home():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@main_bp.route('/profile')
@login_required
def profile():
    return send_from_directory(FRONTEND_DIR, 'profile.html')

@main_bp.route('/<page>')
def static_page(page):
    public_pages = ['login.html', 'signup.html', '404.html']
    protected_pages = ['index.html', 'dashboard.html', 'profile.html']

    if page in protected_pages:
        if not current_user.is_authenticated:
            return redirect('/login')
        return send_from_directory(FRONTEND_DIR, page)

    if page in public_pages:
        return send_from_directory(FRONTEND_DIR, page)
    return send_from_directory(FRONTEND_DIR, '404.html'), 404

@main_bp.route('/styles.css')
def styles():
    return send_from_directory(FRONTEND_DIR, 'styles.css')