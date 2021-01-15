from flask import Flask, render_template, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension

from models import db, connect_db, User, Follows, Character, List, ListCharacter

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


@app.before_request
def add_user_to_g():
    """If user logged in, add to global flask variable"""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

####### ROUTES ###########################

@app.route("/")
def index():
    """Home screen, if not logged in, redirect to registration home screen"""

    if not g.user:
        return redirect("/register-home")

    return render_template("index.html", user=g.user)
