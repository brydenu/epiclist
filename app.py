from flask import Flask, render_template, flash, redirect, session, g, request, jsonify, json
from flask_debugtoolbar import DebugToolbarExtension
import requests
from forms import CreateUserForm, LoginForm, ListForm, EditUserForm
from sqlalchemy.exc import IntegrityError
import os

from models import db, connect_db, User, Follows, Character, List, ListCharacter, DEFAULT_IMAGE_URL

app = Flask(__name__)


# os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///epiclist"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
# os.environ.get('SECRET_KEY', "secretkey2")
app.config["SECRET_KEY"] = "Secret"

toolbar = DebugToolbarExtension(app)
connect_db(app)

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

    lists = List.query.all()
    lists.reverse()

    lists = format_lists(lists)

    return render_template("index.html", lists=lists)

####### LOGIN FUNCTIONS ###############################


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
                image_url=form.image_url.data or DEFAULT_IMAGE_URL
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

    # Get information and add list to db
    if form.validate_on_submit():
        title = form.title.data
        is_ranked = form.is_ranked.data
        is_private = form.is_private.data
        user_id = g.user.id
        characters = form.characters.data

        queries = convert_guids_to_api_queries(characters)

        newList = List(
            title=title,
            user_id=user_id,
            is_ranked=is_ranked,
            is_private=is_private
        )
        db.session.add(newList)
        db.session.commit()

        # Add characters to list
        # Add char ids to a list to iterate later if list is ranked
        char_ids = []
        for q in queries:
            char = initialize_character(q)
            newList.characters.append(char)
            if newList.is_ranked:
                char_ids.append(char.id)

        db.session.commit()

        # Add ranks to characters if list is ranked
        if newList.is_ranked:
            lc = ListCharacter.query.filter(
                ListCharacter.list_id == newList.id).all()
            for index, char in enumerate(char_ids):
                lc[index].rank = index + 1
            db.session.commit()

        return redirect("/")

    return render_template("new_list.html", form=form)


@app.route("/lists/<int:list_id>", methods=["GET"])
def view_list(list_id):
    """Shows full list"""

    lst = List.query.get_or_404(list_id)
    user = g.user
    own_list = False

    if lst.user == user:
        own_list = True

    lst = format_lists(lst)

    return render_template("list.html", user=user, list=lst, own_list=own_list)


def format_lists(lists):
    """Creates list of dictionaries to easily parse list/ranking info in front end"""

    # Get information about rankings of characters
    ranked_lists = []
    if type(lists) == list:
        for lst in lists:

            chars = []
            lc = ListCharacter.query.filter(
                ListCharacter.list_id == lst.id).all()

            for idx, character in enumerate(lst.characters):
                info = {"character": character, "rank": lc[idx].rank}
                chars.append(info)

            char_info = {"list": lst, "characters": chars}
            ranked_lists.append(char_info)
    else:
        chars = []
        lc = ListCharacter.query.filter(
            ListCharacter.list_id == lists.id).all()

        for idx, character in enumerate(lists.characters):
            info = {"character": character, "rank": lc[idx].rank}
            chars.append(info)

        char_info = {"list": lists, "characters": chars}
        return char_info

    return ranked_lists


@app.route("lists/<int:list_id>/delete", methods=["POST"])
def delete_list(list_id):
    """Deletes list"""

    if not g.user:
        flash("You need to be signed in to do that", "danger")
        return redirect("/register-home")

    lst = List.query.get_or_404(list_id)

    if lst.user.user_id != g.user.id:
        flash("You don't have permission to do that", "danger")
        return redirect("/")

    if request.method == 'POST':
        db.session.delete(lst)
        db.session.commit()
        flash("List deleted", "primary")
        return redirect("/")

        ####### CHARACTER FUNCTIONS ###############################


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
    """Checks db for character (if char has beeb previously added),
    if char not added queries API to get character data and creates 
    character in DB"""

    res = requests.get(query, headers=HEADERS)
    data = json.loads(res.text)
    char_info = data["results"]

    char = Character.query.filter(
        Character.guid == char_info["guid"]).all()

    if char:
        return char[0]

    new_char = Character(
        guid=char_info["guid"],
        name=char_info["name"],
        game=game_list_to_string(char_info["games"]),
        image_url=char_info["image"]["thumb_url"]
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
        elif len(games) < 100:
            games = games + ", " + name

    return games


def search_db(char_guid):
    """Searches database of already saved characters for information,
    If no information is found, create a new character instance with the 
    information given."""

    char = Character.query.filter(Character.guid == char_guid).all()

    if char_guid:
        return char[0]


####### USER FUNCTIONS ###############################

@app.route("/users/<username>")
def show_profile(username):
    """Shows user profile"""

    own_profile = False

    if g.user.username == username:
        own_profile = True

    user = User.query.filter(User.username == username).first()
    lists = List.query.filter(List.user_id == user.id).all()
    lists.reverse()

    lists = format_lists(lists)

    return render_template("user.html", own_profile=own_profile, user=user, lists=lists)


@app.route("/users/<username>/edit", methods=["GET", "POST"])
def edit_profile(username):
    """Edit form for user profile"""

    if not g.user:
        flash("You must sign in or register before you can do that", "danger")
        return redirect("/register-home")

    if g.user.username != username:
        flash("You don't have permission to do that", "danger")
        return redirect("/")

    form = EditUserForm(obj=g.user)

    if form.validate_on_submit():
        user = User.authenticate(
            username=g.user.username,
            password=form.password.data
        )
        if user:
            try:
                user.username = form.username.data
                user.image_url = form.image_url.data or DEFAULT_IMAGE_URL
                user.favorite_character = form.favorite_character.data
                db.session.commit()

            except IntegrityError:
                flash("Username taken", "danger")
                return render_template('register.html', form=form)

            do_login(user)
            return redirect("/")

        flash("Invalid password", "danger")
        return render_template("edit-profile.html", form=form)

    return render_template("edit-profile.html", form=form)


@app.route("/users/<username>/delete", methods=["GET", "POST"])
def delete_profile(username):
    """Shows a warning message to confirm deletion"""

    if not g.user:
        flash("You don't have permission to do that", "danger")
        return redirect("/")

    if g.user.username != username:
        flash("You don't have permission to do that", "danger")
        return redirect("/")

    if request.method == 'POST':

        do_logout()
        db.session.delete(g.user)
        db.session.commit()

        return redirect("/register-home")

    return render_template("delete-profile.html")
