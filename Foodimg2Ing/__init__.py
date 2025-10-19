import pymysql
from flask import Flask
from datetime import timedelta

pymysql.install_as_MySQLdb()

# Initialize Flask app
app = Flask(__name__, template_folder='Templates')
app.secret_key = "supersecretkey"
app.permanent_session_lifetime = timedelta(days=5)

# Import routes AFTER app creation
from Foodimg2Ing import routes
