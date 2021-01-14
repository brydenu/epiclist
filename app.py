from flask import Flask, render_template, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy

from models import db, connect_db

app = FLask(__name__)

app.config["SQLALCHEMY_TRACH_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["DEBUG_TB_INTERCEPTS_REDIRECTS"] = False
app.config["SECRET_KEY"] = "secret"

toolbar = DebugToolbarExtension(app)
connect_db(app)

