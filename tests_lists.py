from models import db, connect_db, User, Character, List, ListCharacter, Follows, DEFAULT_IMAGE_URL
from unittest import TestCase
import os
os.environ['DATABASE_URL'] = "postgres:///epiclist_test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class ListTestCase(TestCase):

    """Test List"""

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
    
    def test_create_list(self):
        """Does creating a list add it to the database to become callable?"""
        with self.client as c:

            test_user = User.query.get(11111)
            old_length = len(List.query.all())
            old_user_list_length = len(test_user.lists)

            new_list = List(title="test_list",
                            user_id=11111,
                            is_ranked=False,
                            is_private=True)
            
            db.session.add(new_list)
            db.session.commit()

            new_length = len(List.query.all())
            new_user_list_length = len(test_user.lists)

            self.assertNotEqual(old_length, new_length)
            self.assertNotEqual(old_user_list_length, new_user_list_length)

    def test_private_lists(self):
        """Are private lists only viewable by the list creator?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            list_creator = User.query.get(11111)
            private_list = List(title="private list title",
                                user_id=11111,
                                is_ranked=False,
                                is_private=True)
            
            private_list.id = 123456789
            db.session.add(private_list)
            db.session.commit()
                       
            res = c.get(f"/lists/123456789")

            self.assertEqual(res.status_code, 200)

            # Log in as a user who did not create the list
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 22222
            
            res = c.get(f"/lists/123456789")

            # Should be redirected and thus not allowed to see the private list
            self.assertEqual(res.status_code, 302)

    def test_delete_list(self):
        """Do lists successfully get deleted?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
            
            old_length = len(List.query.all())
            l = List.query.get(111111)

            res = c.post(f"/lists/{l.id}/delete")

            new_length = len(List.query.all())

            self.assertTrue(old_length > new_length)
    
    def test_invalid_delete(self):
        """Are you prevented from deleting a list you didn't make?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user2.id
            
            old_length = len(List.query.all())
            l = List.query.get(111111)

            res = c.post(f"/lists/{l.id}/delete")

            new_length = len(List.query.all())

            self.assertEqual(old_length, new_length)
            self.assertEqual(res.status_code, 302)
    
    def test_edit_list_access(self):
        """Are you allowed to edit a list you made?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            l = List.query.get(111111)
            res = c.get("/lists/111111/edit")

            self.assertEqual(res.status_code, 200)
    
    def test_edit_list_invalid_user(self):
        """Are you prevented from editing a list you didn't make?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user2.id
            
            l = List.query.get(111111)
            res = c.get("/lists/111111/edit")

            self.assertEqual(res.status_code, 302)
    
    def test_repr(self):
        """Does the __repr__ display as expected?"""

        l = List.query.first()
        expected = "<List Instance | List ID: 111111 | Name: title1 | User ID: 11111>"

        self.assertEqual(expected, str(l))

