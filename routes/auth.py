from flask import request, redirect, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from models import db, User
from routes import auth_bp
import urllib.parse

def redirect_with_message(path, error=None, success=None):
    if error:
        return redirect(f'{path}?error={urllib.parse.quote(error)}')
    if success:
        return redirect(f'{path}?success={urllib.parse.quote(success)}')
    return redirect(path)

@auth_bp.route('/register', methods=['POST'])
def register():
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')
    confirm_password = request.form.get('confirm-password', '')
    
    if not all([first_name, last_name, email, password]):
        return redirect_with_message('/signup', error='All fields are required')
    
    if password != confirm_password:
        return redirect_with_message('/signup', error='Passwords do not match')
    
    if len(password) < 8:
        return redirect_with_message('/signup', error='Password must be at least 8 characters')
    
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return redirect_with_message('/signup', error='Email already registered')
    
    user = User(first_name=first_name, last_name=last_name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    return redirect_with_message('/login', success='Account created successfully! Please log in.')

@auth_bp.route('/login', methods=['POST'])
def login():
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')
    remember = request.form.get('remember') == 'on'
    
    if not email or not password:
        return redirect_with_message('/login', error='Email and password are required')
    
    user = User.query.filter_by(email=email).first()
    
    if user and user.check_password(password):
        login_user(user, remember=remember)
        next_page = request.form.get('next', '/index')
        return redirect(next_page)
    
    return redirect_with_message('/login', error='Invalid email or password')

@auth_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    return redirect_with_message('/login', success='You have been logged out')

@auth_bp.route('/user', methods=['GET'])
def get_user():
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'id': current_user.id,
            'email': current_user.email,
            'first_name': current_user.first_name,
            'last_name': current_user.last_name
        })
    return jsonify({'authenticated': False})