from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


App = Flask(__name__) #instance is Uppercase, folder is lowercase
App.config.from_object(Config)
db = SQLAlchemy(App) #database created
db.init_app(App)
migrate = Migrate(App,db) #migration repository
login = LoginManager(App) 
login.login_view = 'login'



from app import routes, models, errors #scripts that we created
