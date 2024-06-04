from flask import Flask 
import os
import db
import recipes
from dotenv import load_dotenv

app = Flask(__name__)
test = load_dotenv()  # take environment variables from .env.
db.init_app(app)


app.register_blueprint(recipes.bp)

print(test)
if __name__ == '__main__':
    app.run()
