"""Seed file to make sample data for blogly db."""

from models import User, db, Post
from app import app

with app.app_context():

    # Create all tables
    db.drop_all()
    db.create_all()

    # If table isn't empty, empty it
    User.query.delete()

    # Add users
    summer = User(first_name='Summer', last_name='Winter')
    alan = User(first_name='Alan', last_name='Alda')
    joel = User(first_name='Joel', last_name='Burton')
    jane = User(first_name='Jane', last_name='Smith')

    # Add new user objects to session, so they'll persist
    db.session.add_all([summer, alan, joel, jane])

    # Commit -- otherwise, this never gets saved!
    db.session.commit()

    # Add posts
    summer_p1 = Post(title='Flask Is Awesome', content='I love flask and SQLAlchemy', user=summer)
    summer_p2 = Post(title='I love icecream', content='Summer is here. Summer wants to eat lots of icecream!', user=summer)
    alan_p1 = Post(title='International Dog Day', content='Today is my favorite day of the year. Let''s celebrate human''s best friends!', user=alan)
    joel_p1 = Post(title='IG complaint', content='IG is an overrated app. Its algorithm sucks people in and is bad for content creators', user=joel)
    joel_p2 = Post(title='My cat', content='My cat is my best friend. Who resonates?', user=joel)
    jane_p1 = Post(title='Learning SQLAlchemy', content='I have been learning flask-sqlalchemy for the last month or so. I can already create some interesting applications. I can''t wait to see where this will lead me to in the near future!', user=jane)
    jane_p2 = Post(title='My turtle', content='I had two turtles when I was a kid, but I didn''t know how to take care of them, so one of them died and I still feel guilty about it until today! May your soul rest in peace, my beloved turtle.', user=jane)
    jane_p3 = Post(title='Orion', content='Orion is a bratty pit/shepherd mix with a very cute fake-lab face!', user=jane)

    # add posts and commit
    db.session.add_all([summer_p1, summer_p2, alan_p1, joel_p1, joel_p2, jane_p1, jane_p2, jane_p3])
    db.session.commit()
