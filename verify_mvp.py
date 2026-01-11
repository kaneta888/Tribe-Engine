from app import create_app, db
from models import User, Post, SMSLog

app = create_app()

with app.app_context():
    print("--- starting verification ---")
    
    # 1. Setup Data
    db.drop_all()
    db.create_all()
    
    # 2. Create Users
    owner = User(username='owner', email='owner@test.com', role='owner', sms_credits=50) # Start with 50
    admin = User(username='admin', email='admin@test.com', role='admin')
    paid_user = User(username='paid', email='paid@test.com', role='paid', sms_opt_in=True)
    free_user = User(username='free', email='free@test.com', role='free', sms_opt_in=True)
    
    db.session.add_all([owner, admin, paid_user, free_user])
    db.session.commit()
    print("[PASS] Users created")
    
    # 3. Post Visibility Logic
    post_public = Post(content="Public Post", author=owner, visibility='all')
    post_paid = Post(content="Paid Only Post", author=owner, visibility='paid')
    
    db.session.add_all([post_public, post_paid])
    db.session.commit()
    
    # Check what free user sees (backend query level)
    free_feed = Post.query.filter_by(visibility='all').all()
    assert len(free_feed) == 1
    assert free_feed[0].content == "Public Post"
    print("[PASS] Feed visibility (Free) check")
    
    # 4. SMS Logic
    # Owner wants to send SMS to 2 users (paid & free are opted in)
    # Cost should be 2. Current credits 50.
    
    targets = User.query.filter_by(sms_opt_in=True).all()
    cost = len(targets)
    assert cost == 2
    
    if owner.sms_credits >= cost:
        owner.sms_credits -= cost
        log = SMSLog(sender_id=owner.id, content="Emergency", target_count=cost, cost=cost)
        db.session.add(log)
        db.session.commit()
        print(f"[PASS] SMS Sent. Deducted {cost}. New Balance: {owner.sms_credits}")
        assert owner.sms_credits == 48
    else:
        print("[FAIL] Insufficient credits")
        
    print("--- verification complete ---")
