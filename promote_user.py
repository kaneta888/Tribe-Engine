from app import create_app
from extensions import db
from models import User

app = create_app()
with app.app_context():
    # Promote the last registered user (the one the user just made) to Owner
    user = User.query.order_by(User.id.desc()).first()
    if user:
        print(f"Found user: {user.username} (Current Role: {user.role})")
        user.role = 'owner'
        user.sms_credits = 100  # Give them credits to test SMS
        db.session.commit()
        print(f"Successfully promoted {user.username} to OWNER.")
    else:
        print("No users found.")
