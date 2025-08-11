# config.py
import os
from dotenv import load_dotenv
load_dotenv()

# production values come from Render env vars; defaults are safe fallbacks
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-do-not-use-in-prod")
SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
# allow string False/True from env; convert to boolean safely
SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", "False").lower() in ("1","true","yes")
