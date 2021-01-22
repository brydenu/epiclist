from flask import Flask, render_template, flash, redirect, session, g, request, jsonify, json
from flask_debugtoolbar import DebugToolbarExtension
import requests
from forms import CreateUserForm, LoginForm
from sqlalchemy.exc import IntegrityError

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
CURR_USER_USERNAME = "curr_user_username"


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

####### USER FUNCTIONS ###############################


@app.route("/register-home")
def show_register_home():
    """Shows register home page (not the actual register form)"""

    if g.user:
        return redirect("/")

    return render_template("register-home.html")


@app.route("/register", methods=["GET", "POST"])
def show_register():
    """Shows register form if GET. Attempts to create user and add to db if POST"""

    form = CreateUserForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                image_url=form.image_url.data
            )
            db.session.commit()
        except IntegrityError:
            flash("Username taken", "danger")
            return render_template('register.html', form=form)

        do_login(user)
        return redirect("/")

    else:
        return render_template('register.html', form=form)


@app.route("/login", methods=["GET", "POST"])
def show_login():
    """Shows login form if GET. Attempts to authenticate data if POST."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(
            username=form.username.data,
            password=form.password.data
        )
        if user:
            do_login(user)
            return redirect("/")
        else:
            flash("Invalid username or password", "danger")
            return render_template("login.html", form=form)

    else:
        return render_template("login.html", form=form)


@app.route("/logout", methods=["GET"])
def logout():
    """Route to logout user"""

    if not g.user:
        flash("You need to be signed in to do that", "danger")
        return redirect("/register-home")

    do_logout()
    return redirect("/register-home")


def do_login(user):
    """Logs in user (authentication happens in route)"""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Clears session variable"""

    del session[CURR_USER_KEY]

####### LIST FUNCTIONS ###############################

# @app.route("/lists", methods=["GET"])
# def show_lists():


@app.route("/lists/new", methods=["GET", "POST"])
def create_list():
    """Shows create list form if GET. Submits new list if POST"""

    if not g.user:
        flash("You need to be signed in to do that", "danger")
        return redirect("/register-home")

    return render_template("new_list.html")


# GETTING TO INFORMATION
# get response --> res
# get the text from the response --> text = res.text
# format the text --> data = json.loads(text)
# get to information --> results = data["results"]
# results NOW HAS ALL INFORMATION OF ALL RESULTS
# TO GRAB FIRST RESULT --> res1 = results[0]
# TO GET NAME aliases = res1["aliases"]
# IF MULTIPLE NAMES THIS WILL HAVE TO HAVE AN ALGO TO GET NAME

@app.route("/search-characters", methods=["POST"])
def search_api():
    """Accepts request from the front end to look for new characters from the API"""

    # if not g.user:
    #     flash("You need to be signed in to do that", "danger")
    #     return redirect("/register-home")
    req = request.json
    data = json.loads(req["data"])

    api_query = data["query"]

    print(api_query)

    headers = {"User-Agent": "EpicListSearchBot"}

    res = requests.get(api_query, headers=headers)
    data = json.loads(res.text)
    search_results = data["results"]

    char_list = []

    for index, result in enumerate(search_results):
        name = search_results[index]['name']
        image_url_lg = search_results[index]['image']['thumb_url']
        image_url_sm = search_results[index]['image']['tiny_url']
        game = search_results[index]['first_appeared_in_game']['name']
        api_id = search_results[index]['id']

        character = {
            "name": name,
            "image_url_lg": image_url_lg,
            "image_url_sm": image_url_sm,
            "game": game,
            "api_id": api_id}

        char_list.append(character)

    character_results = {"character_results": char_list}
    return jsonify(character_results)
