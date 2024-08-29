"""Blogly application."""

from flask import Flask, redirect, render_template, request, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, Tag, PostTag
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
    tags = Tag.query.all()
    return render_template('add_post.html', user=user, tags=tags)

@app.route('/users/<int:user_id>/posts/new', methods=['POST'])
def submit_new_post(user_id):
    """Get info from add new post form, save to database, redirect to the user's detail page."""
    post_title = request.form['ptitle']
    post_content = request.form['pcontent']
    post_user_id = user_id
    new_post = Post(title=post_title, content=post_content, user_id=post_user_id)

    # add tags-posts relationship
    for key in request.form.keys():
        if key.startswith('tag-'):
            tag_id = int(key[4:])
            tag = Tag.query.get(tag_id)
            new_post.tags.append(tag)

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
    tags = Tag.query.all()
    return render_template('edit_post.html', post=post, tags=tags)

@app.route('/posts/<int:post_id>/edit', methods=['POST'])
def submit_post_edit(post_id):
    """Get info from post edit page, update database, redirect back to the post detail page."""
    post = Post.query.get_or_404(post_id)
    post.title = request.form['ptitle']
    post.content = request.form['pcontent']
    post.created_at = datetime.now(timezone.utc)

    # Update post-tag relationship
    current_tag_ids = [tag.id for tag in post.tags]
    new_tag_ids = [int(id) for id in request.form.getlist('tags')]
    combined_tag_ids = set(current_tag_ids + new_tag_ids)
    tag_ids_2_delete = [id for id in combined_tag_ids if (id in current_tag_ids) and (id not in new_tag_ids)]
    tag_ids_2_add = [id for id in combined_tag_ids if (id not in current_tag_ids) and (id in new_tag_ids)]
    # delete tags that are no longer checked by user
    for tag_id in tag_ids_2_delete:
        PostTag.query.filter_by(post_id=post.id, tag_id=tag_id).delete()
    # Add new tags
    for tag_id in tag_ids_2_add:
        post.posts_tags.append(PostTag(post_id=post.id, tag_id=tag_id))

    db.session.add(post)
    db.session.commit()

    # add flash message for success in editing a post
    flash('Your post was modified!')
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

@app.route('/tags')
def list_all_tags():
    """A page to list all available tags."""
    all_tags = Tag.query.all()
    return render_template('list_tags.html', tags=all_tags)

@app.route('/tags/<int:tag_id>')
def show_tag_details(tag_id):
    tag = Tag.query.get(tag_id)
    return render_template('tag_details.html', tag=tag)

@app.route('/tags/new')
def add_tag():
    all_posts = Post.query.all()
    return render_template('add_tag.html', posts=all_posts)

@app.route('/tags/new', methods=['POST'])
def submit_new_tag():
    tag_name = request.form['tname']
    new_tag = Tag(name=tag_name)

    for post_id in request.form.getlist('posts'):
        new_tag.posts.append(Post.query.get(int(post_id)))

    db.session.add(new_tag)
    db.session.commit()

    # flash a message to user for successful tag edit
    flash(f'Tag {tag_name} has been added.')

    return redirect('/tags')

@app.route('/tags/<int:tag_id>/edit')
def edit_tag(tag_id):
    tag = Tag.query.get(tag_id)
    all_posts = Post.query.all()
    return render_template('edit_tag.html', tag=tag, posts=all_posts)

@app.route('/tags/<int:tag_id>/edit', methods=['POST'])
def submit_tag_edit(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    tag.name = request.form['tname']

    # Update posts linked to this tag
    current_post_ids = [post.id for post in tag.posts]
    new_post_ids = [int(id) for id in request.form.getlist('posts')]
    combined_post_ids = set(current_post_ids + new_post_ids)
    post_ids_2_delete = [id for id in combined_post_ids if id in current_post_ids and id not in new_post_ids]
    post_ids_2_add = [id for id in combined_post_ids if id not in current_post_ids and id in new_post_ids]
    # delete unchecked ids
    for id in post_ids_2_delete:
        PostTag.query.filter_by(post_id=id, tag_id=tag_id).delete()
    # add newly checked ids
    for id in post_ids_2_add:
        tag.posts_tags.append(PostTag(post_id=id, tag_id=tag_id))

    db.session.add(tag)
    db.session.commit()

    # flash a message to user for successful tag edit
    flash(f'Tag {tag.name} has been modified.')
    return redirect('/tags')

@app.route('/tags/<int:tag_id>/delete', methods=['POST'])
def delete_tag(tag_id):
    Tag.query.filter_by(id=tag_id).delete()
    db.session.commit()

    # flash a message to indicate the tag has been deleted
    flash(f'Tag with id={tag_id} has been deleted.')
    return redirect('/tags')

@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 not found page."""
    return render_template('not_found_page.html'), 404
