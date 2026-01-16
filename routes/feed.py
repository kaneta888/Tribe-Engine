import os
import secrets
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models import Post
from services.storage import get_storage_provider

feed_bp = Blueprint('feed', __name__)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    
    storage = get_storage_provider()
    return storage.save(form_picture, picture_fn)

@feed_bp.route('/feed')
@login_required
def feed():
    # Role-based visibility logic
    if current_user.is_paid_user():
        # See all posts
        posts = Post.query.order_by(Post.created_at.desc()).all()
    else:
        # See only public posts
        posts = Post.query.filter_by(visibility='all').order_by(Post.created_at.desc()).all()
    
    return render_template('feed.html', posts=posts)

@feed_bp.route('/post/new', methods=['POST'])
@login_required
def create_post():
    content = request.form.get('content')
    visibility = request.form.get('visibility', 'all')
    image_file = request.files.get('image')
    
    if not content:
        flash('Post content cannot be empty', 'error')
        return redirect(url_for('feed.feed'))
        
    image_path = None
    if image_file and image_file.filename:
        image_path = save_picture(image_file)
        
    post = Post(
        content=content, 
        author=current_user,
        visibility=visibility,
        image_path=image_path
    )
    
    db.session.add(post)
    db.session.commit()
    
    flash('Post created!', 'success')
    return redirect(url_for('feed.feed'))

@feed_bp.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def toggle_like(post_id):
    from models import Like
    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    
    if like:
        db.session.delete(like)
    else:
        new_like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(new_like)
        
    db.session.commit()
    
    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'status': 'success',
            'is_liked': not bool(like),
            'like_count': post.like_count
        })
        
    return redirect(url_for('feed.feed', _anchor=f'post-{post_id}'))

@feed_bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    from models import Comment
    content = request.form.get('content')
    if not content:
        flash('コメントを入力してください', 'error')
        return redirect(url_for('feed.feed'))
        
    comment = Comment(content=content, author=current_user, post_id=post_id)
    db.session.add(comment)
    db.session.commit()
    
    return redirect(url_for('feed.feed', _anchor=f'post-{post_id}'))

@feed_bp.route('/post/<int:post_id>/save', methods=['POST'])
@login_required
def toggle_save(post_id):
    from models import SavedPost
    post = Post.query.get_or_404(post_id)
    saved = SavedPost.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    
    if saved:
        db.session.delete(saved)
    else:
        new_save = SavedPost(user_id=current_user.id, post_id=post_id)
        db.session.add(new_save)
        
    db.session.commit()
    
    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'status': 'success',
            'is_saved': not bool(saved)
        })

    return redirect(url_for('feed.feed', _anchor=f'post-{post_id}'))

@feed_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user and not current_user.is_admin():
        abort(403)
    
    db.session.delete(post)
    db.session.commit()
    flash('Post has been deleted!', 'success')
    return redirect(url_for('feed.feed'))
