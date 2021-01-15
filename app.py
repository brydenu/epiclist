from flask import Flask, render_template, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from forms import CreateUserForm, LoginForm
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, User, Follows, Character, List, ListCharacter, DEFAULT_IMAGE_URL

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = 'postgres:///epiclist'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["DEBUG_TB_INTERCEPTS_REDIRECTS"] = False
app.config["SECRET_KEY"] = "secret"

toolbar = DebugToolbarExtension(app)
connect_db(app)
db.create_all()

CURR_USER_KEY = "curr_user"
g.DEFAULT_IMAGE = DEFAULT_IMAGE_URL

@app.before_request
def add_user_to_g():
    """If user logged in, add to global flask variable"""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

####### GENERAL ROUTES ###########################

@app.route("/")
def index():
    """Home screen, if not logged in, redirect to registration home screen"""

    if not g.user:
        return redirect("/register-home")

    return render_template("index.html", user=g.user)

####### USER ROUTES ###############################

@app.route("/register-home")
def show_register_home():
    """Shows register home page (not the actual register form)"""

    if g.user:
        return redirect("/")
    
    return render_template("register-home.html")

@app.route("/register", methods=["GET, POST"])
def register():
    """Shows register form if GET. Attempts to create user and add to db if POST"""

    form = CreateUserForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                image_url=form.image_url.data or g.DEFAULT_IMAGE
            )
            db.session.commit()
        except IntegrityError:
            flash("Username taken", "danger")
            return render_template('register.html', form=form)
        
        login_user(user)

        return redirect("/")
    
    else:
        return render_template('register.html', form=form)
        

