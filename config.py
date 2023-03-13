import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or "extremelysecretkey666"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False #False to not send every change to our flask file
    POSTS_PER_PAGE = 5 #specifies posts per paginate page in forum and explore
    ENTRIES_PER_PAGE = 7 #specified entries per page for bookmarks and history
