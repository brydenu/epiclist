from models import db, connect_db, User, Character, List, ListCharacter, Follows, DEFAULT_IMAGE_URL
from unittest import TestCase
from flask import json
import os
import requests
os.environ['DATABASE_URL'] = "postgres:///epiclist_test"

from app import app, CURR_USER_KEY, HEADERS, format_list, format_lists, convert_guids_to_api_queries, organize_characters, initialize_character, game_list_to_string

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class HelperFunctionsTestCase(TestCase):

    """Test helper functions including those that interact with the
    giantbomb API"""

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

        char1 = Character(guid="3005-177",
                        name="Mario",
                        game="Super Mario 64",
                        image_url="fake-image-of-mario"
        )
        self.char1_id = 1111
        char1.id = self.char1_id
        db.session.add(char1)

        char2 = Character(guid="3005-191",
                        name="Link",
                        game="The Legend of Zelda",
                        image_url="fake-image-of-link"
        )
        self.char2_id = 2222
        char2.id = self.char2_id
        db.session.add(char2)

        char3 = Character(guid="3005-73",
                        name="Sonic the Hedgehog",
                        game="Sonic the Hedgehog Game",
                        image_url="fake-image-of-sonic"
        )
        self.char3_id = 3333
        char3.id = self.char3_id
        db.session.add(char3)

        list1 = List(title="title1",
                            user_id="11111",
                            is_ranked=True,
                            is_private=False
        )
        list1.id = 111111

        list1.characters.append(char1)
        list1.characters.append(char2)
        list1.characters.append(char3)

        db.session.add(list1)
        
        list2 = List(title="title2",
                            user_id="22222",
                            is_ranked=False,
                            is_private=False
        )
        list2.id = 222222

        list2.characters.append(char2)
        list2.characters.append(char3)

        db.session.add(list2)

        db.session.commit()

        lcs = ListCharacter.query.filter(ListCharacter.list_id == list1.id).all()
        lcs[0].rank = 1
        lcs[1].rank = 2
        lcs[2].rank = 3

        db.session.commit()
    
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res


    def test_format_list_ranked(self):
        """Does format_list format a single list properly for a ranked list?"""

        list1 = List.query.get(111111)

        l = format_list(list1)

        expected1 = "{'list': <List Instance | List ID: 111111 | Name: title1 | User ID: 11111>,"
        expected2 = "'characters': [{'character': <Character Instance | ID: 1111 | Name: Mario | Game: Super Mario 64>, 'rank': 1}, {'character': <Character Instance | ID: 2222 | Name: Link | Game: The Legend of Zelda>, 'rank': 2}, {'character': <Character Instance | ID: 3333 | Name: Sonic the Hedgehog | Game: Sonic the Hedgehog Game>, 'rank': 3}]}"

        self.assertIn(expected1, str(l))
        self.assertIn(expected2, str(l))

    def test_format_list_unranked(self):
        """Does format_list format a single list properly for an unranked list?"""

        list2 = List.query.get(222222)

        l = format_list(list2)

        expected1 = "{'list': <List Instance | List ID: 222222 | Name: title2 | User ID: 22222>,"
        expected2 = "'characters': [{'character': <Character Instance | ID: 2222 | Name: Link | Game: The Legend of Zelda>, 'rank': None}, {'character': <Character Instance | ID: 3333 | Name: Sonic the Hedgehog | Game: Sonic the Hedgehog Game>, 'rank': None}]}"

        self.assertIn(expected1, str(l))
        self.assertIn(expected2, str(l))

    def test_format_lists_single(self):
        """Does format_lists correctly work if given only a single list?"""

        list1 = List.query.get(111111)

        l = format_lists(list1)

        expected1 = "{'list': <List Instance | List ID: 111111 | Name: title1 | User ID: 11111>,"
        expected2 = "'characters': [{'character': <Character Instance | ID: 1111 | Name: Mario | Game: Super Mario 64>, 'rank': 1}, {'character': <Character Instance | ID: 2222 | Name: Link | Game: The Legend of Zelda>, 'rank': 2}, {'character': <Character Instance | ID: 3333 | Name: Sonic the Hedgehog | Game: Sonic the Hedgehog Game>, 'rank': 3}]}"

        self.assertIn(expected1, str(l))
        self.assertIn(expected2, str(l))

    def test_format_lists_multiple(self):
        """Does format_lists correctly work if givena list of lists?"""

        lists = List.query.all()

        l = format_lists(lists)
        
        expected1 = "{'list': <List Instance | List ID: 222222 | Name: title2 | User ID: 22222>,"
        expected2 = "'characters': [{'character': <Character Instance | ID: 2222 | Name: Link | Game: The Legend of Zelda>, 'rank': None}, {'character': <Character Instance | ID: 3333 | Name: Sonic the Hedgehog | Game: Sonic the Hedgehog Game>, 'rank': None}]}"
        expected3 = "{'list': <List Instance | List ID: 111111 | Name: title1 | User ID: 11111>,"
        expected4 = "'characters': [{'character': <Character Instance | ID: 1111 | Name: Mario | Game: Super Mario 64>, 'rank': 1}, {'character': <Character Instance | ID: 2222 | Name: Link | Game: The Legend of Zelda>, 'rank': 2}, {'character': <Character Instance | ID: 3333 | Name: Sonic the Hedgehog | Game: Sonic the Hedgehog Game>, 'rank': 3}]}"

        self.assertIn(expected1, str(l))
        self.assertIn(expected2, str(l))
        self.assertIn(expected3, str(l))
        self.assertIn(expected4, str(l))
    
    def test_convert_guids_to_api_queries(self):
        """Does the function take a string of guids and create an object containing a
        formatted query ready to call the API with along with a the guid to check
        the epiclist database with?"""

        test_guid_string = "3005-177, 3005-191, 3005-73"
        result = convert_guids_to_api_queries(test_guid_string)
        expected1 = "[{'guid': '3005-177', 'query': 'https://www.giantbomb.com/api/character/3005-177/?api_key=7257597392c1160f53ddc5354ec336518380ec17&format=json'},"
        expected2 = "{'guid': '3005-191', 'query': 'https://www.giantbomb.com/api/character/3005-191/?api_key=7257597392c1160f53ddc5354ec336518380ec17&format=json'}," 
        expected3 = "{'guid': '3005-73', 'query': 'https://www.giantbomb.com/api/character/3005-73/?api_key=7257597392c1160f53ddc5354ec336518380ec17&format=json'}]"

        self.assertIn(expected1, str(result))
        self.assertIn(expected2, str(result))
        self.assertIn(expected3, str(result))


    def test_initialize_character_new(self):
        """Does the function create a new table row if the character has
        an unfamiliar guid?"""

        query = convert_guids_to_api_queries("3005-370")[0]

        char_table_len = len(Character.query.all())

        # The first assertion shows this method is valid for testing if a character is in our db
        # The second proves a character with the guid 170 is not in our db right now
        self.assertTrue(Character.query.filter(Character.guid == "3005-177").first())
        self.assertFalse(Character.query.filter(Character.guid == "3005-370").first())

        char = initialize_character(query)
        new_table_len = len(Character.query.all())
        expected = f"<Character Instance | ID: {char.id} | Name: Luigi | Game: {char.game}>"

        self.assertTrue(new_table_len > char_table_len)
        self.assertEqual(expected, str(char))
        self.assertTrue(Character.query.filter(Character.guid == "3005-370").first())
    

    def test_initialize_existing_character(self):
        """Does the function not call the API, and instead pull information just from
        the epiclist characters table if the character already exists in the db?"""

        query = convert_guids_to_api_queries("3005-177")[0]

        char_table_len = len(Character.query.all())

        # Character should already be in the database
        self.assertTrue(Character.query.filter(Character.guid == "3005-177").first())

        char = initialize_character(query)
        new_table_len = len(Character.query.all())
        expected = f"<Character Instance | ID: 1111 | Name: Mario | Game: Super Mario 64>"

        self.assertTrue(new_table_len == char_table_len)
        self.assertEqual(expected, str(char))
        self.assertTrue(Character.query.filter(Character.guid == "3005-177").first())
    
    def test_organize_characters_ranked_new(self):
        """Does the function organize and rank characters of a new ranked list?"""

        l = List(title="organize_test_list",
                user_id=11111,
                is_ranked=True,
                is_private=False)
        l.id = 123456789
        
        char1 = Character.query.get(1111)
        char2 = Character.query.get(2222)
        char3 = Character.query.get(3333)

        db.session.add(l)

        guid_string = f"{char1.guid}, {char2.guid}, {char3.guid}"

        queries = convert_guids_to_api_queries(guid_string)

        organize_characters(queries, l, True)

        mario_lc = ListCharacter.query.filter(ListCharacter.list_id == 123456789).filter(ListCharacter.character_id == 1111).first()
        link_lc = ListCharacter.query.filter(ListCharacter.list_id == 123456789).filter(ListCharacter.character_id == 2222).first()
        sonic_lc = ListCharacter.query.filter(ListCharacter.list_id == 123456789).filter(ListCharacter.character_id == 3333).first()

        self.assertEqual(mario_lc.rank, 1)
        self.assertEqual(link_lc.rank, 2)
        self.assertEqual(sonic_lc.rank, 3)
        self.assertEqual(len(l.characters), 3)
        self.assertIn(str(char1), str(l.characters))
        self.assertIn(str(char2), str(l.characters))
        self.assertIn(str(char3), str(l.characters))
    
    def test_organize_characters_unranked_new(self):
        """Does the function add all characters of a new unranked list and omit ranks?"""

        l = List(title="organize_test_list",
                user_id=11111,
                is_ranked=False,
                is_private=False)
        l.id = 123456789
        
        char1 = Character.query.get(1111)
        char2 = Character.query.get(2222)
        char3 = Character.query.get(3333)

        db.session.add(l)

        guid_string = f"{char1.guid}, {char2.guid}, {char3.guid}"

        queries = convert_guids_to_api_queries(guid_string)

        organize_characters(queries, l, True)

        mario_lc = ListCharacter.query.filter(ListCharacter.list_id == 123456789).filter(ListCharacter.character_id == 1111).first()
        link_lc = ListCharacter.query.filter(ListCharacter.list_id == 123456789).filter(ListCharacter.character_id == 2222).first()
        sonic_lc = ListCharacter.query.filter(ListCharacter.list_id == 123456789).filter(ListCharacter.character_id == 3333).first()

        self.assertEqual(mario_lc.rank, None)
        self.assertEqual(link_lc.rank, None)
        self.assertEqual(sonic_lc.rank, None)
        self.assertEqual(len(l.characters), 3)
        self.assertIn(str(char1), str(l.characters))
        self.assertIn(str(char2), str(l.characters))
        self.assertIn(str(char3), str(l.characters))

    def test_organize_characters_ranked_existing(self):
        """Does the function rerank characters accurately from an existing list?"""

        list1 = List.query.get(111111)
        
        mario_old_rank = ListCharacter.query.filter(ListCharacter.list_id == 111111).filter(ListCharacter.character_id == 1111).first().rank
        link_old_rank = ListCharacter.query.filter(ListCharacter.list_id == 111111).filter(ListCharacter.character_id == 2222).first().rank
        sonic_old_rank = ListCharacter.query.filter(ListCharacter.list_id == 111111).filter(ListCharacter.character_id == 3333).first().rank

        char1 = Character.query.get(1111)
        char2 = Character.query.get(2222)
        char3 = Character.query.get(3333)

        guid_string = f"{char2.guid}, {char3.guid}, {char1.guid}"

        queries = convert_guids_to_api_queries(guid_string)

        organize_characters(queries, list1, False)

        mario_new_rank = ListCharacter.query.filter(ListCharacter.list_id == 111111).filter(ListCharacter.character_id == 1111).first().rank
        link_new_rank = ListCharacter.query.filter(ListCharacter.list_id == 111111).filter(ListCharacter.character_id == 2222).first().rank
        sonic_new_rank = ListCharacter.query.filter(ListCharacter.list_id == 111111).filter(ListCharacter.character_id == 3333).first().rank
        
        self.assertEqual(mario_new_rank, 3)
        self.assertEqual(link_new_rank, 1)
        self.assertEqual(sonic_new_rank, 2)
        self.assertNotEqual(mario_old_rank, mario_new_rank)
        self.assertNotEqual(link_old_rank, link_new_rank)
        self.assertNotEqual(sonic_old_rank, sonic_new_rank)
        self.assertEqual(len(list1.characters), 3)
        self.assertIn(str(char1), str(list1.characters))
        self.assertIn(str(char2), str(list1.characters))
        self.assertIn(str(char3), str(list1.characters))

    def test_game_list_to_string(self):
        """Does the function create a correctly formatted string of games?"""

        query = convert_guids_to_api_queries("3005-2616")
        res = requests.get(query[0]["query"], headers=HEADERS)
        data = json.loads(res.text)
        game_list = data["results"]["games"]

        game_list_string = game_list_to_string(game_list)

        expected = "Carmen Sandiego Adventures in Math: The Lady Liberty Larceny, Where in the World is Carmen Sandiego?"

        self.assertEqual(expected, game_list_string)



