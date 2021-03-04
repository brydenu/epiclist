from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()

DEFAULT_IMAGE_URL = "https://www.edmundsgovtech.com/wp-content/uploads/2020/01/default-picture_0_0.png"


def connect_db(app):
    """Connect db to flask app"""

    db.app = app
    db.init_app(app)


class Follows(db.Model):
    """User to user connection based on who is following who"""

    __tablename__ = 'follows'

    user_being_followed = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete="cascade"), primary_key=True)

    user_following = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete="cascade"), primary_key=True)
    
    def __repr__(self):
        return f"<Follow Instance | Being Followed: {self.user_being_followed} | Follower: {self.user_following}>"


class User(db.Model):
    """User information"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(20), nullable=False, unique=True)

    image_url = db.Column(db.Text, default=DEFAULT_IMAGE_URL)

    bio = db.Column(db.Text, nullable=True)

    password = db.Column(db.Text, nullable=False)

    favorite_character = db.Column(db.Text, nullable=True)

    followers = db.relationship("User",
                                secondary="follows",
                                primaryjoin=(
                                    Follows.user_being_followed == id),
                                secondaryjoin=(Follows.user_following == id)
                                )

    following = db.relationship("User",
                                secondary="follows",
                                primaryjoin=(Follows.user_following == id),
                                secondaryjoin=(
                                    Follows.user_being_followed == id)
                                )

    lists = db.relationship('List', cascade="all, delete", backref="user")

    def __repr__(self):
        """Representation of instances"""
        return f"<User Instance | ID: {self.id} | Username: {self.username}>"

    def following_ids(self):
        """Returns a list of user ids that this user is following"""

        ids = []
        for usr in self.following:
            ids.append(usr.id)

        return ids

    def public_lists(self):
        """Returns all public lists"""

        return List.query.filter(List.user_id == self.id).filter(
            List.is_private == False).all()

    @classmethod
    def signup(cls, username, password, image_url=DEFAULT_IMAGE_URL):
        """Creates user with hashed password"""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pwd,
            image_url=image_url
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Authenticates user with saved password hash.

        Returns False if user/password combo don't match"""

        user = cls.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user

        return False


class List(db.Model):
    """Lists created by users"""

    __tablename__ = "lists"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(50), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete="CASCADE"), nullable=False)

    is_ranked = db.Column(db.Boolean, nullable=False)

    is_private = db.Column(db.Boolean, nullable=False)

    characters = db.relationship('Character', secondary="lists_characters")

    def __repr__(self):
        """Representation of instance"""
        return f"<List Instance | List ID: {self.id} | Name: {self.title} | User ID: {self.user_id}>"


class Character(db.Model):
    """Characters to be added to lists"""

    __tablename__ = "characters"

    id = db.Column(db.Integer, primary_key=True)

    guid = db.Column(db.Text, nullable=True)

    name = db.Column(db.Text, nullable=False)

    game = db.Column(db.Text, nullable=False)

    image_url = db.Column(db.Text, nullable=True)

    def __repr__(self):
        """Representation of instance"""
        return f"<Character Instance | ID: {self.id} | Name: {self.name} | Game: {self.game}>"


class ListCharacter(db.Model):
    """Connection between List and Character"""

    __tablename__ = "lists_characters"

    id = db.Column(db.Integer, primary_key=True)

    character_id = db.Column(db.Integer, db.ForeignKey(
        'characters.id', ondelete="CASCADE"), nullable=False)

    list_id = db.Column(db.Integer, db.ForeignKey(
        'lists.id', ondelete="CASCADE"), nullable=False)

    rank = db.Column(db.Integer, nullable=True)

    characters = db.relationship('Character', backref="lists_characters")

    def __repr__(self):
        """Represention of instance"""
        return f"<ListCharacter Instance | ID: {self.id} | Character: {self.character_id} ({self.characters.name}) | List: {self.list_id} | Rank in list: {self.rank}>"
