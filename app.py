from flask import Flask, render_template, redirect, url_for
from extensions import db, login_manager, migrate
from config import Config

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config.from_object(Config)

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    login_manager.login_view = 'auth.login'

    with app.app_context():
        # Import models to ensure they are registered
        from models import User, Post, Comment, SMSLog
        
        # Create database tables (for MVP simplicity)
        db.create_all()

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.feed import feed_bp
    from routes.user import user_bp
    from routes.admin import admin_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(feed_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    
    # Alias for profile -> settings to match base.html link
    app.add_url_rule('/profile', endpoint='profile', view_func=lambda: redirect(url_for('user.settings')))

    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))

    @app.route('/')
    def index():
        return render_template('index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001)
