from models import db, connect_db, User, Character, List, ListCharacter, Follows, DEFAULT_IMAGE_URL
from unittest import TestCase
import os
os.environ['DATABASE_URL'] = "postgres:///epiclist_test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class CharactersTestCase(TestCase):

    """Test Characters"""
    def setUp(self):

        char1 = Character(guid="3005-177",
                        name="Mario",
                        game="Super Mario 64",
                        image_url="fake-image-of-mario"
        )
        self.char1_id = 1111
        char1.id = self.char1_id

        db.session.add(char1)
        db.session.commit()
         
    
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_repr(self):
        """Does the __repr__ display as expected?"""

        char = Character.query.get(1111)
        expected = "<Character Instance | ID: 1111 | Name: Mario | Game: Super Mario 64>"

        self.assertEqual(expected, str(char))

