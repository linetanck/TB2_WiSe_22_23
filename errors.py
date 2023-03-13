from flask import render_template
from app import App, db

@App.errorhandler(404) #works similar to view function
def not_found_error(error): #if its an error 404 it returns template for that error
    return render_template('404.html'), 404 #404 means server not found

@App.errorhandler(500)
def internal_error(error):
    db.session.rollback() #to make sure failed database session doesnt interfere with template database session
    return render_template('500.html'), 500 #second value needs to be returned because default is 200 which means successful response
