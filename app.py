from flask import Flask, render_template, flash, redirect, session, g, request, jsonify, json
from flask_debugtoolbar import DebugToolbarExtension
import requests
from forms import CreateUserForm, LoginForm, ListForm
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
db.drop_all()
db.create_all()

CURR_USER_KEY = "curr_user"
CURR_USER_USERNAME = "curr_user_username"
HEADERS = {"User-Agent": "EpicListSearchBot"}


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

    form = ListForm()
    if form.validate_on_submit():
        # WHAT I NEED HERE:
        # should accept: characters from request
        # should take: information from form for title, ranked, private
        # Should create a list object and return properties to front-end
        title = form.title.data
        is_ranked = form.is_ranked.data
        is_private = form.is_private.data
        user_id = g.user.id
        characters = form.characters.data

        queries = convert_guids_to_api_queries(characters)
        print(queries)

        newList = List(
            title=title,
            user_id=user_id,
            is_ranked=is_ranked,
            is_private=is_private
        )

        db.session.add(newList)
        db.session.commit()

        return redirect("/")

    return render_template("new_list.html", form=form)

####### CHARACTER FUNCTIONS ###############################

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

    if not g.user:
        flash("You need to be signed in to do that", "danger")
        return redirect("/register-home")

    # Get information from request from front-end
    req = request.json
    data = json.loads(req["data"])

    # Information to send in request
    api_query = data["query"]

    # Send request and unpack information
    res = requests.get(api_query, headers=HEADERS)
    data = json.loads(res.text)
    search_results = data["results"]

    char_list = []

    # Take only the information neeeded and create objects to add to a
    # list that will be displayed on front end
    for index, result in enumerate(search_results):
        name = search_results[index]['name']
        image_url_lg = search_results[index]['image']['thumb_url']
        image_url_sm = search_results[index]['image']['tiny_url']
        game = search_results[index]['first_appeared_in_game']['name']
        guid = search_results[index]['guid']

        character = {
            "name": name,
            "image_url_lg": image_url_lg,
            "image_url_sm": image_url_sm,
            "game": game,
            "guid": guid,
            "guid": guid}

        char_list.append(character)

    # Send to front end
    character_results = {"character_results": char_list}
    return jsonify(character_results)


def convert_guids_to_api_queries(guid_string):
    """Converts guid string received from front end and turns it into a list
    of api queries to send to giantbomb"""

    guid_list = guid_string.split(", ")

    query_list = []
    for guid in guid_list:
        query = f"https://www.giantbomb.com/api/character/{guid}/?api_key=7257597392c1160f53ddc5354ec336518380ec17&format=json"
        query_list.append(query)

    return query_list


def initialize_character(query):
    """Queries API to get character data and creates character in DB"""

    res = requests.get(query, headers=HEADERS)
    data = json.loads(res.text)
    char_info = data["results"]

    new_char = Character(
        guid=char_info["guid"]
        name=char_info["name"]
        game=game_list_to_string(char_info["games"])
        description=char_info["description"]
    )

    db.session.add(new_char)
    db.session.commit()

    return new_char


def game_list_to_string(game_list):
    """Converts list of games a character has appeared in to a string to store in db"""

    games = ""
    for game in game_list:
        name = game["name"]
        if games == "":
            games = name
        else:
            games = games + ", " + name

    return games


def query_list_to_api(query_list):
    """"""

    for


def search_db(character):
    """Searches database of already saved characters for information,
    If no information is found, create a new character instance with the 
    information given."""
