import re
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from extensions import db, login_manager
from models import User, Group, Membership

main_bp = Blueprint('main', __name__)


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    if user is None:
        login_manager.unauthorized()
    return user


@main_bp.route('/')
@login_required
def index():
    from flask_login import current_user
    return render_template('index.html', first_name=current_user.first_name)


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        errors = []

        if not email:
            errors.append('Email is required.')
        if not password:
            errors.append('Password is required.')

        if not errors:
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                from flask_login import login_user
                login_user(user, remember=bool(remember))
                next_page = request.args.get('next')
                flash(f'Welcome back, {user.first_name}!', 'success')
                return redirect(next_page or url_for('main.index'))
            else:
                errors.append('Invalid email or password.')

        for error in errors:
            flash(error, 'error')

    return render_template('login.html')


@main_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        errors = []

        if not first_name:
            errors.append('First name is required.')
        if not last_name:
            errors.append('Last name is required.')
        if not email:
            errors.append('Email is required.')
        elif not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            errors.append('Please enter a valid email address.')
        if not password:
            errors.append('Password is required.')
        elif len(password) < 8:
            errors.append('Password must be at least 8 characters.')
        if password != confirm_password:
            errors.append('Passwords do not match.')

        if email:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                errors.append('An account with this email already exists.')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('signup.html',
                                   first_name=first_name,
                                   last_name=last_name,
                                   email=email)

        user = User(email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('main.login'))

    return render_template('signup.html')


@main_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    from flask_login import logout_user
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    from flask_login import current_user

    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')

        errors = []

        if not current_password:
            errors.append('Current password is required to save changes.')
        elif not current_user.check_password(current_password):
            errors.append('Current password is incorrect.')

        if not first_name:
            errors.append('First name is required.')
        if not last_name:
            errors.append('Last name is required.')

        if new_password and len(new_password) < 8:
            errors.append('New password must be at least 8 characters.')

        if errors:
            for error in errors:
                flash(error, 'error')
        else:
            current_user.first_name = first_name
            current_user.last_name = last_name
            if new_password:
                current_user.set_password(new_password)
                from flask_login import logout_user
                db.session.commit()
                logout_user()
                flash('Profile updated. Please log in with your new password.', 'success')
                return redirect(url_for('main.login'))
            db.session.commit()
            flash('Profile updated successfully.', 'success')

        return render_template('profile.html',
                               first_name=first_name or current_user.first_name,
                               last_name=last_name or current_user.last_name,
                               email=current_user.email,
                               created_at=current_user.created_at)

    return render_template('profile.html',
                           first_name=current_user.first_name,
                           last_name=current_user.last_name,
                           email=current_user.email,
                           created_at=current_user.created_at)


@main_bp.route('/groups/create', methods=['POST'])
@login_required
def create_group():
    name = request.form.get('group_name', '').strip()
    currency = request.form.get('currency', '').strip()

    if not name:
        flash('Group name is required.', 'error')
        return redirect(url_for('main.index'))

    try:
        group = Group(
            name=name,
            currency=currency,
            invite_code=Group.generate_invite_code(),
            created_by=current_user.id,
        )
        db.session.add(group)
        db.session.flush()

        membership = Membership(
            user_id=current_user.id,
            group_id=group.id,
            role='admin',
        )
        db.session.add(membership)
        db.session.commit()

        flash(f'Group "{name}" created successfully!', 'success')
    except Exception:
        db.session.rollback()
        flash('Failed to create group. Please try again.', 'error')

    return redirect(url_for('main.index'))


@main_bp.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
