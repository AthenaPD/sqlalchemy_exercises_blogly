from unittest import TestCase
from app import app
from models import db, User, Post, Tag, PostTag

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

with app.app_context():
    db.drop_all()
    db.create_all()


class UserViewsTestCase(TestCase):
    """Tests for views for Users."""

    def setUp(self):
        """Add a sample user"""
        with app.app_context():
            User.query.delete()

            user = User(first_name='Test', last_name='User')
            db.session.add(user)
            db.session.commit()

            self.user_id = user.id

    def tearDown(self):
        """Clean up any fouled transaction."""
        with app.app_context():
            db.session.rollback()

    def test_list_users(self):
        with app.test_client() as client:
            response = client.get("/users")
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('Test User', html)

    def test_show_user_details(self):
        with app.test_client() as client:
            response = client.get(f'/users/{self.user_id}')
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('<h1>Test User</h1>', html)

    def test_delete_user(self):
        with app.test_client() as client:
            response = client.post(f'/users/{self.user_id}/delete', follow_redirects=True)
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn("<h1>Users</h1>", html)
            self.assertNotIn("Test User", html)

    def test_add_user_form(self):
        with app.test_client() as client:
            response = client.get('/users/new')
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn("<h1>Create a user</h1>", html)

    def test_add_user(self):
        with app.test_client() as client:
            new_user = {"first_name": "Toothless", "last_name": "Hiccup"}
            response = client.post("/users/new", data=new_user, follow_redirects=True)
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn("Toothless Hiccup", html)


class PostViewsTestCase(TestCase):
    """Tests for views for Posts."""

    def setUp(self):
        """Add a sample user and post"""
        with app.app_context():
            User.query.delete()
            Post.query.delete()

            user = User(first_name='Test', last_name='User')
            db.session.add(user)
            db.session.commit()

            self.user_id = user.id

            post = Post(title='Test Post', content='This is a test post.', user_id=self.user_id)
            db.session.add(post)
            db.session.commit()
            self.post_id = post.id

    def tearDown(self):
        """Clean up any fouled transaction."""
        with app.app_context():
            db.session.rollback()

    def test_add_post(self):
        """Test creating a post."""
        with app.test_client() as client:
            post_data = {'title': 'Test Post II', 'content': 'This is yet another test.', 'user_id': self.user_id}
            response = client.post(f'/users/{self.user_id}/posts/new', data=post_data, follow_redirects=True)
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn("Test Post II", html)

    def test_delete_post(self):
        """Test deleting a post."""
        with app.test_client() as client:
            response = client.post(f'/posts/{self.post_id}/delete', follow_redirects=True)
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn("<h1>Test User</h1>", html)
            self.assertNotIn("Test Post", html)

    def test_edit_post(self):
        """Test view function to edit a post."""
        with app.test_client() as client:
            post_data = {'title': 'Test Post I', 'content': 'This is a modified test post.'}
            response = client.post(f'/posts/{self.post_id}/edit', data=post_data, follow_redirects=True)
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn("<h1>Test User</h1>", html)
            self.assertIn("Test Post I", html)

    def test_show_post_details(self):
        """Test view function to show a post's details."""
        with app.test_client() as client:
            response = client.get(f'/posts/{self.post_id}')
            html = response.get_data(as_text=True)
            
            self.assertEqual(response.status_code, 200)
            self.assertIn("<h1>Test Post</h1>", html)


class TagViewsTestCase(TestCase):
    """Test view functions for tags."""

    def setUp(self):
        """Add a sample user and post"""
        with app.app_context():
            User.query.delete()
            Post.query.delete()
            Tag.query.delete()

            user = User(first_name='Test', last_name='User')
            db.session.add(user)
            db.session.commit()

            self.user_id = user.id

            post = Post(title='Test Post', content='This is a test post.', user_id=self.user_id)
            db.session.add(post)
            db.session.commit()
            self.post_id = post.id

            tag = Tag(name='Test')
            db.session.add(tag)
            db.session.commit()
            self.tag_id = tag.id

            post_tag = PostTag(post_id=self.post_id, tag_id=self.tag_id)
            db.session.add(post_tag)
            db.session.commit()

    def tearDown(self):
        """Clean up any fouled transaction."""
        with app.app_context():
            db.session.rollback()

    def test_add_tag(self):
        """Test creating a tag."""
        with app.test_client() as client:
            tag_data = {'name': 'Flask Testing', 'posts': [self.post_id]}
            response = client.post(f'/tags/new', data=tag_data, follow_redirects=True)
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn("Flask Testing", html)

    def test_delete_tag(self):
        """Test deleting a tag."""
        with app.test_client() as client:
            response = client.post(f'/tags/{self.tag_id}/delete', follow_redirects=True)
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn("<h1>Tags</h1>", html)
            self.assertNotIn("Test", html)

    def test_show_tag_detials(self):
        """Test view function to show a tag's details."""
        with app.test_client() as client:
            response = client.get(f'/tags/{self.tag_id}')
            html = response.get_data(as_text=True)
            
            self.assertEqual(response.status_code, 200)
            self.assertIn("<h1>Test</h1>", html)
            self.assertIn('Test Post', html)

    def test_show_all_tags(self):
        """Test view function to list all tags."""
        with app.test_client() as client:
            response = client.get('/tags')
            html = response.get_data(as_text=True)
            
            self.assertEqual(response.status_code, 200)
            self.assertIn("<h1>Tags</h1>", html)
            self.assertIn('Test', html)
