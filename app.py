"""Blogly application."""

from flask import Flask, redirect, render_template, request, flash
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
    """Show the add a new user form."""
    return render_template('add_user.html')

@app.route('/users/new', methods=['POST'])
def submit_new_user():
    """Get info from the add new user form, save info to database, redirect to all-users page."""
    first_name = request.form['fname']
    last_name = request.form['lname']
    image_url = request.form['image-url'] if request.form['image-url'] else None

    new_user = User(first_name=first_name, last_name=last_name, image_url=image_url)
    db.session.add(new_user)
    db.session.commit()

    # add flash message for success in adding user
    flash(f'User {first_name} {last_name} was created successfully!')

    return redirect('/users')

@app.route('/users/<int:user_id>')
def show_user_details(user_id):
    """Show details of a user and a list of his/her posts"""
    user = User.query.get_or_404(user_id)
    return render_template('user_details.html', user=user)

@app.route('/users/<int:user_id>/edit')
def edit_user_form(user_id):
    """Edit user info page."""
    user = User.query.get(user_id)
    return render_template('edit_user.html', user=user)

@app.route('/users/<int:user_id>/edit', methods=['POST'])
def submit_user_edit(user_id):
    """Get info from edit user page, update database, redirect back to all-users page."""
    user = User.query.get(user_id)
    user.first_name = request.form['fname']
    user.last_name = request.form['lname']
    user.image_url = request.form['image-url']
    db.session.add(user)
    db.session.commit()

    # add flash message for success in editing user
    flash(f'User {user.first_name} {user.last_name} was modified!')

    return redirect('/users')

@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """Delete user and redirect back to all-users page."""
    User.query.filter_by(id=user_id).delete()
    db.session.commit()

    # add flash message for success in deleting user
    flash(f'User with an id of {user_id} was deleted!')
    return redirect('/users')

@app.route('/users/<int:user_id>/posts/new')
def new_post_form(user_id):
    """Add a new post form."""
    user = User.query.get(user_id)
    return render_template('new_post_form.html', user=user)

@app.route('/users/<int:user_id>/posts/new', methods=['POST'])
def submit_new_post(user_id):
    """Get info from add new post form, save to database, redirect to the user's detail page."""
    post_title = request.form['ptitle']
    post_content = request.form['pcontent']
    post_user_id = user_id
    new_post = Post(title=post_title, content=post_content, user_id=post_user_id)
    db.session.add(new_post)
    db.session.commit()

    # add flash message for success in adding a new post
    flash('A new post was successfully created!')
    return redirect(f'/users/{user_id}')

@app.route('/posts/<int:post_id>')
def show_post_details(post_id):
    """Page to show the detailed content of a post."""
    post = Post.query.get(post_id)
    return render_template('post_details.html', post=post)

@app.route('/posts/<int:post_id>/edit')
def edit_post_form(post_id):
    """Page to edit a post."""
    post = Post.query.get(post_id)
    return render_template('edit_post.html', post=post)

@app.route('/posts/<int:post_id>/edit', methods=['POST'])
def submit_post_edit(post_id):
    """Get info from post edit page, update database, redirect back to the post detail page."""
    post = Post.query.get(post_id)
    post.title = request.form['ptitle']
    post.content = request.form['pcontent']
    post.created_at = datetime.now(timezone.utc)
    db.session.add(post)
    db.session.commit()

    # add flash message for success in editing a post
    flash('Your Post was modified!')
    return redirect(f'/posts/{post_id}')

@app.route('/posts/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    """delete a post, update database, redirect to user detail page."""
    user_id = Post.query.get(post_id).user.id
    Post.query.filter_by(id=post_id).delete()
    db.session.commit()

    # add flash message for success in deleting a post
    flash(f'Your post was deleted!')
    return redirect(f'/users/{user_id}')

@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 not found page."""
    return render_template('not_found_page.html'), 404
