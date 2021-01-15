from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequred, Length

class CreateUserForm(FlaskForm):
    """Form for registering a new user"""

    username = StringField('Username', validators=[DataRequred()])
    password = PasswordField('Password', validators=[DataRequred()])
    image_url = StringField('(Optional) Image URL')

class LoginForm(FlaskForm):
    """Login user form"""

    username = StringField('Username', validators=[DataRequred()])
    password = PasswordField('Password', validators=[DataRequred()])
