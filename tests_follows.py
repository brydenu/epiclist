from models import db, connect_db, User, Character, List, ListCharacter, Follows, DEFAULT_IMAGE_URL
from unittest import TestCase
import os
os.environ['DATABASE_URL'] = "postgres:///epiclist_test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class FollowsTestCase(TestCase):

    """Test Follows"""

    def setUp(self):

        User.query.delete()
        List.query.delete()
        ListCharacter.query.delete()

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

    def test_follow_user(self):
        """Can you follow another user if you are signed in?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
            
            test_user = User.query.get(11111)
            followed_user = User.query.get(22222)
            
            old_following_len = len(test_user.following)
            
            res = c.post("/users/22222/follow")

            new_following_len = len(test_user.following)

            self.assertTrue(new_following_len > old_following_len)
            self.assertIn(followed_user, test_user.following)
    
    def test_unfollow_user(self):
        """Does unfollowing work?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
            
            test_user = User.query.get(11111)
            followed_user = User.query.get(22222)

            empty_following_len = len(test_user.following)
            
            res1 = c.post("/users/22222/follow")

            test_user = User.query.get(11111)
            after_following_len = len(test_user.following)

            self.assertTrue(after_following_len > empty_following_len)
            self.assertIn(followed_user, test_user.following)

            res = c.post("/users/22222/unfollow")

            test_user = User.query.get(11111)
            after_unfollow_len = len(test_user.following)

            self.assertTrue(after_unfollow_len < after_following_len)
            self.assertTrue(after_unfollow_len == empty_following_len)
            self.assertNotIn(followed_user, test_user.following)

    def test_repr(self):
        """Does the __repr__ display as expectd?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
            
            c.post("/users/22222/follow")
        
        f = Follows.query.first()
        expected = "<Follow Instance | Being Followed: 22222 | Follower: 11111>"
        
        self.assertEqual(expected, str(f))


            
    



            