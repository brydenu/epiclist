from models import db, connect_db, User, Character, List, ListCharacter, Follows, DEFAULT_IMAGE_URL
from unittest import TestCase
import os
os.environ['DATABASE_URL'] = "postgres:///epiclist_test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class UserViewsTestCase(TestCase):

    """Test views for user"""

    def setUp(self):

        User.query.delete()
        Character.query.delete()
        List.query.delete()
        ListCharacter.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        self.user1 = User.signup(username="tester1",
                                    password="password123")
        self.user1.id = 11111

        self.user2 = User.signup(username="tester2",
                                    password="password321",
                                    image_url="fake-image-url")
        self.user2.id = 22222
                        
        self.user3 = User.signup(username="tester3",
                                    password="password",
                                    image_url="another-fake-image")
        self.user3.id = 33333
        
        self.user4 = User.signup(username="tester4",
                                    password="password2")
        self.user4.id = 44444

        list1 = List(title="title1",
                            user_id="11111",
                            is_ranked=True,
                            is_private=False
        )
        list1.id = 111111

        db.session.add(list1)

        db.session.commit()
    
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_redirect_register_home(self):
        """Does the view redirect from everywhere but individual lists when not signed in?"""
        with self.client as c:

            res = c.get("/")
            self.assertEqual(res.status_code, 302)

            res = c.get("/users/tester1")
            self.assertEqual(res.status_code, 302)

            res = c.get("/lists/111111")
            self.assertEqual(res.status_code, 200)

    def test_register_home(self):
        """Does the view show the welcome page if not signed in?"""
        with self.client as c:

            res = c.get("/register-home")
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("Welcome to EpicList", html)
            self.assertNotIn('<nav class="navbar navbar-custom border-bottom border-light navbar-expand-md navbar-dark sticky-top">', html)
    
    def test_show_register_page(self):
        """Does the view show the register page and all of the forms?"""
        with self.client as c:

            res = c.get("/register")
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("Already have an account?", html)
            self.assertNotIn('<nav class="navbar navbar-custom border-bottom border-light navbar-expand-md navbar-dark sticky-top">', html)

    def test_show_login_page(self):
        """Does the view show the login page and the forms?"""
        with self.client as c:

            res = c.get("/login")
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("Don't have an account?", html)
    
    def test_show_list_not_signed_in(self):
        """Does the view let you see a list without having an account?"""
        with self.client as c:

            res = c.get("/lists/111111")
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("title1", html)
            self.assertIn("tester1", html)
            self.assertNotIn('<nav class="navbar navbar-custom border-bottom border-light navbar-expand-md navbar-dark sticky-top">', html)
    
    def test_show_index_signed_in(self):
        """Does the view show the home page when signed in?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            res = c.get("/")
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<nav class="navbar navbar-custom border-bottom border-light navbar-expand-md navbar-dark sticky-top">', html)
            self.assertIn('<a href="/users/tester1">tester1</a>', html)
            self.assertIn('All Lists', html)
            self.assertIn(DEFAULT_IMAGE_URL, html)
    
    def test_show_private_lists_valid(self):
        """Does the view show a seperate page of private lists from a user
        if that is the currently signed in user?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
            
            res = c.get("/users/tester1/private-lists")

            self.assertEqual(res.status_code, 200)

    def test_show_private_lists_invalid(self):
        """Does the view redirect users who are trying to see private lists
        of a user who is not themselves (signed in)?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user2.id
            
            res = c.get("/users/tester1/private-lists")

            self.assertEqual(res.status_code, 302)

        