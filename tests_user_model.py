from models import db, connect_db, User, Character, List, ListCharacter, Follows, DEFAULT_IMAGE_URL
from unittest import TestCase
import os
os.environ['DATABASE_URL'] = "postgres:///epiclist_test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserTestCase(TestCase):
    """Tests user functions"""

    def setUp(self):

        User.query.delete()
        List.query.delete()
        
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


    def test_signup(self):
        """Does User.signup() successfully create a new user with
        the correct information and add it to the database?
        (Tests DEFAULT_IMAGE_URL as well)"""
        with self.client as c:

            old_length = len(User.query.all())

            test_user = User.signup(username="test_username",
                        password="test_password")
            
            test_user.id = 123456789
            
            db.session.commit()
            new_length = len(User.query.all())

            self.assertNotEqual(new_length, old_length)

            # Does the model give a default user image to users without an image_url?
            self.assertEqual(test_user.image_url, DEFAULT_IMAGE_URL)
    
    def test_authenticate(self):
        """Does the authentication process work as expected?"""
        with self.client as c:

            test_user = self.user1

            auth_test1 = User.authenticate(test_user.username, "password123")
            auth_test2 = User.authenticate("tester1", "password123")
            auth_test3 = User.authenticate("tester1", "password124")
            auth_test4 = User.authenticate("tester2", "password321")
            auth_test5 = User.authenticate("tester2", "password123")

            self.assertEqual(auth_test1, test_user)
            self.assertEqual(auth_test2, test_user)
            self.assertEqual(auth_test3, False)
            self.assertEqual(auth_test4, self.user2)
            self.assertEqual(auth_test5, False)
        
    def test_repr(self):
        """Does the repr display in the expected format?"""

        test_user1 = User.query.get(11111)
        test_user2 = User.query.get(22222)
        test_user3 = User.query.get(33333)
        test_user4 = User.query.get(44444)

        expected1 = f"<User Instance | ID: {test_user1.id} | Username: {test_user1.username}>"
        expected2 = f"<User Instance | ID: {test_user2.id} | Username: {test_user2.username}>"
        expected3 = f"<User Instance | ID: {test_user3.id} | Username: {test_user3.username}>"
        expected4 = f"<User Instance | ID: {test_user4.id} | Username: {test_user4.username}>"

        self.assertEqual(str(test_user1), expected1)
        self.assertEqual(str(test_user2), expected2)
        self.assertEqual(str(test_user3), expected3)
        self.assertEqual(str(test_user4), expected4)
    
    def test_public_lists(self):
        """Does the method to return public lists work correctly?"""
        with self.client as c:
            
            # Create a private list to see if the method differentiates the two:
            private_list = List(title="private list title",
                                user_id=11111,
                                is_ranked=False,
                                is_private=True)
            
            db.session.add(private_list)
            db.session.commit()

            test_user = User.query.get(11111)
            total_lists_length = len(test_user.lists)
            public_lists_length = len(test_user.public_lists())

            self.assertTrue(public_lists_length > 0)
            self.assertNotEqual(total_lists_length, public_lists_length)






                

            