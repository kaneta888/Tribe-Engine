from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import User

user_bp = Blueprint('user', __name__)

@user_bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@user_bp.route('/settings/update', methods=['POST'])
@login_required
def update_profile():
    email = request.form.get('email')
    phone_number = request.form.get('phone_number')
    sms_opt_in = request.form.get('sms_opt_in') == 'on'
    
    existing_email = User.query.filter_by(email=email).first()
    if existing_email and existing_email.id != current_user.id:
        flash('Email already in use.', 'error')
        return redirect(url_for('user.settings'))
        
    current_user.email = email
    current_user.phone_number = phone_number
    current_user.sms_opt_in = sms_opt_in
    
    db.session.commit()
    flash('Profile updated successfully.', 'success')
    return redirect(url_for('user.settings'))

@user_bp.route('/settings/toggle-subscription', methods=['POST'])
@login_required
def toggle_sub():
    if current_user.role == 'free':
        current_user.role = 'paid'
        flash('Upgraded to Paid!', 'success')
    elif current_user.role == 'paid':
        current_user.role = 'free'
        flash('Downgraded to Free.', 'info')
        
    db.session.commit()
    return redirect(url_for('user.settings'))
