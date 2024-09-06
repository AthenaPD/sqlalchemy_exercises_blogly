"""Models for Blogly."""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

def connect_db(app):
    """Connect to database."""
    db.app = app
    db.init_app(app)


class User(db.Model):
    """User model."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String, nullable=False, default='https://images.unsplash.com/photo-1724094505377-ac01c7813010?q=80&w=2574&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D')

    posts = db.relationship('Post', backref='user', cascade='all, delete', passive_deletes=True)

    def __repr__(self):
        return f'<User id={self.id} name={self.full_name}>'
    
    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    

class Post(db.Model):
    """Post model."""

    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))

    posts_tags = db.relationship('PostTag', backref='post')
    tags = db.relationship('Tag', secondary='posts_tags', backref='posts')

    def __repr__(self):
        return f'<Post id={self.id} title={self.title} user={self.user_id}>'
    
    @property
    def formatted_date(self):
        return f"{self.created_at.strftime('%a %b %d %Y, %I:%M %p')}"


class Tag(db.Model):
    """Tag model."""

    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    posts_tags = db.relationship('PostTag', backref='tag', cascade='all, delete', passive_deletes=True)

    def __repr__(self):
        return f'<Tag id={self.id} name={self.name}>'


class PostTag(db.Model):
    """Model for the table to connect posts and tags table (M2M relationship)."""

    __tablename__ = "posts_tags"

    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)

    def __repr__(self):
        return f'<Post id={self.post_id}, Tag id={self.tag_id}>'
