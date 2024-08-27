"""Blogly application."""

from flask import Flask, redirect, render_template, request
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post
from datetime import datetime, timezone

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'Orion'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)

@app.route('/')
def root():
    """Home/root page."""
    posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    # raise
    return render_template('home_page.html', posts=posts)

@app.route('/users')
def list_users():
    """Show a list of all users in the db"""
    users = User.query.order_by('last_name', 'first_name').all()
    return render_template('list_users.html', users=users)

@app.route('/users/new')
def add_user_form():
    return render_template('add_user.html')

@app.route('/users/new', methods=['POST'])
def submit_new_user():
    first_name = request.form['fname']
    last_name = request.form['lname']
    image_url = request.form['image-url'] if request.form['image-url'] else None

    new_user = User(first_name=first_name, last_name=last_name, image_url=image_url)
    db.session.add(new_user)
    db.session.commit()

    # add flash message for success in adding user

    return redirect('/users')

@app.route('/users/<int:user_id>')
def show_user_details(user_id):
    user = User.query.get(user_id)
    return render_template('user_details.html', user=user)

@app.route('/users/<int:user_id>/edit')
def edit_user_form(user_id):
    user = User.query.get(user_id)
    return render_template('edit_user.html', user=user)

@app.route('/users/<int:user_id>/edit', methods=['POST'])
def submit_user_edit(user_id):
    user = User.query.get(user_id)
    user.first_name = request.form['fname']
    user.last_name = request.form['lname']
    user.image_url = request.form['image-url']
    db.session.add(user)
    db.session.commit()

    return redirect('/users')

@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    User.query.filter_by(id=user_id).delete()
    db.session.commit()
    return redirect('/users')

@app.route('/users/<int:user_id>/posts/new')
def new_post_form(user_id):
    user = User.query.get(user_id)
    return render_template('new_post_form.html', user=user)

@app.route('/users/<int:user_id>/posts/new', methods=['POST'])
def submit_new_post(user_id):
    post_title = request.form['ptitle']
    post_content = request.form['pcontent']
    post_user_id = user_id
    new_post = Post(title=post_title, content=post_content, user_id=post_user_id)
    db.session.add(new_post)
    db.session.commit()
    return redirect(f'/users/{user_id}')

@app.route('/posts/<int:post_id>')
def show_post_details(post_id):
    post = Post.query.get(post_id)
    return render_template('post_details.html', post=post)

@app.route('/posts/<int:post_id>/edit')
def edit_post_form(post_id):
    post = Post.query.get(post_id)
    return render_template('edit_post.html', post=post)

@app.route('/posts/<int:post_id>/edit', methods=['POST'])
def submit_post_edit(post_id):
    post = Post.query.get(post_id)
    post.title = request.form['ptitle']
    post.content = request.form['pcontent']
    post.created_at = datetime.now(timezone.utc)
    db.session.add(post)
    db.session.commit()
    return redirect(f'/posts/{post_id}')

@app.route('/posts/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    user_id = Post.query.get(post_id).user.id
    Post.query.filter_by(id=post_id).delete()
    db.session.commit()
    return redirect(f'/users/{user_id}')
