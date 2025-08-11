# app.py
import os
from flask import Flask, render_template
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# config values from config.py (no import of app inside config.py)
import config
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS

# models.py should define db = SQLAlchemy() (no app argument)
# then initialize it here so imports don't circularly depend on app
import models
models.db.init_app(app)

# import routes after app and db are ready
import routes   # or router.py — use the real filename in your repo

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
