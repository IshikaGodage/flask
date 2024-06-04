import click
import mysql.connector
import os

from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    if "db" not in g or not g.db.is_connected():
        # connect to the database
        
        g.db = mysql.connector.connect(
            host=os.environ["DB_HOST"],
            user=os.environ["DB_USERNAME"],
            passwd=os.environ["DB_PASSWORD"],
            db=os.environ["DB_DATABASE"]
        )
        
    return g.db

def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        # close the database 
        db.close()

def init_app(app):
    app.teardown_appcontext(close_db)
    
