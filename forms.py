from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Length


class CreateUserForm(FlaskForm):
    """Form for registering a new user"""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    image_url = StringField('(Optional) Image URL')


class EditUserForm(FlaskForm):
    """Form to edit user info. Has more fields than thbe registration form"""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    image_url = StringField('(Optional) Image URL')
    favorite_character = StringField("(Optional) Favorite Character")
    bio = TextAreaField("(Optional) Bio")


class LoginForm(FlaskForm):
    """Login user form"""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class ListForm(FlaskForm):
    """Create/modify list form"""

    title = StringField('Title', validators=[DataRequired()])
    is_ranked = BooleanField('Ranked')
    is_private = BooleanField('Private')
    characters = HiddenField(validators=[DataRequired()])
