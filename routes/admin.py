from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from extensions import db
from models import User, SMSLog

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
@login_required
def require_admin():
    if not current_user.is_admin():
        abort(403)

@admin_bp.route('/')
def dashboard():
    users = User.query.all()
    opted_in_count = User.query.filter_by(sms_opt_in=True).count()
    sms_logs = SMSLog.query.order_by(SMSLog.timestamp.desc()).limit(5).all()
    return render_template('admin/dashboard.html', users=users, opted_in_count=opted_in_count, sms_logs=sms_logs)

@admin_bp.route('/user/<int:user_id>/role', methods=['POST'])
def update_role(user_id):
    if not current_user.is_owner() and not current_user.is_admin():
         abort(403)
         
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    
    # Safety: Only owner can make admins/owners
    if new_role in ['admin', 'owner'] and not current_user.is_owner():
        flash('Only Owners can promote to Admin/Owner', 'error')
        return redirect(url_for('admin.dashboard'))
        
    user.role = new_role
    db.session.commit()
    flash(f'Updated {user.username} role to {new_role}', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/sms/send', methods=['POST'])
def send_sms():
    confirm = request.form.get('confirm_send')
    message = request.form.get('message')
    
    if confirm != 'SEND':
        flash('Confirmation failed. Type "SEND" exactly.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    # Calculate Cost
    targets = User.query.filter_by(sms_opt_in=True).all()
    count = len(targets)
    cost = count * 1 # 1 credit per user
    
    if count == 0:
        flash('No users have opted in for SMS.', 'warning')
        return redirect(url_for('admin.dashboard'))
        
    if current_user.sms_credits < cost:
        flash(f'Insufficient credits. Need {cost}, have {current_user.sms_credits}.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    # Deduct Logic
    current_user.sms_credits -= cost
    
    # Log
    log = SMSLog(
        sender_id=current_user.id,
        content=message,
        target_count=count,
        cost=cost
    )
    db.session.add(log)
    db.session.commit()
    
    # Mock Sending Logic (Integration point for Twilio)
    print(f"--- MOCK SMS SENDING ---")
    print(f"Message: {message}")
    print(f"Targets: {[u.phone_number for u in targets]}")
    print(f"------------------------")
    
    flash(f'SMS Sent successfully to {count} users. Cost: {cost} credits.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/credits/add', methods=['POST'])
def add_credits():
    if not current_user.is_owner():
        abort(403)
        
    current_user.sms_credits += 100
    db.session.commit()
    flash('Added 100 credits.', 'success')
    return redirect(url_for('admin.dashboard'))
