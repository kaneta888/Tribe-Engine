from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        avatar_file = request.files.get('avatar')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('auth.register'))
            
        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'error')
            return redirect(url_for('auth.register'))
            
        # Handle avatar upload
        avatar_path = None
        if avatar_file and avatar_file.filename:
            from routes.feed import save_picture
            avatar_path = save_picture(avatar_file)
        
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password, method='pbkdf2:sha256'),
            avatar_path=avatar_path
        )
        
        # First user is Owner
        if User.query.count() == 0:
            new_user.role = 'owner'
            new_user.sms_credits = 100 # Default credits for owner
        
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('feed.feed'))
        
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('feed.feed'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            flash('Please check your login details and try again.', 'error')
            return redirect(url_for('auth.login'))
            
        login_user(user)
        return redirect(url_for('feed.feed'))
        
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate reset token
            import secrets
            from datetime import datetime, timedelta
            
            token = secrets.token_urlsafe(32)
            user.reset_token = token
            user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()
            
            # Send email (mock for now)
            from services.email_service import send_password_reset_email
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            send_password_reset_email(user.email, reset_url)
            
        # Always show success message (security: don't reveal if email exists)
        flash('パスワードリセット用のリンクをメールで送信しました。', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    from datetime import datetime
    
    user = User.query.filter_by(reset_token=token).first()
    
    # Verify token exists and is not expired
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        flash('このリンクは無効または期限切れです。', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('パスワードが一致しません。', 'error')
            return render_template('reset_password.html')
        
        # Update password and clear token
        user.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()
        
        flash('パスワードが正常に変更されました。', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('reset_password.html')
