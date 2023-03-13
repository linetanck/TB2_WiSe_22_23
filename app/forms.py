from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, RadioField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User

class LoginForm(FlaskForm): #fields to login a user
    username = StringField('Username', validators = [DataRequired()])
    password = PasswordField('Password', validators = [DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm): #fields to create new users
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username): #checks if username is already taken
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email): #checks if email is already used for other user
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username #username stored in instance variable because user could change other info except username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first() #checks again if username is taken
            if user is not None:
                raise ValidationError('Please use a different username.')

class PostForm(FlaskForm):
    post = TextAreaField('Make a suggestion', validators=[DataRequired()])
    submit = SubmitField('Submit')

class EmptyForm(FlaskForm): #for following
    submit = SubmitField('Submit')

class DisclaimerForm(FlaskForm):
    checkbox = BooleanField('I have read and understood the above disclaimer and my own responsibility.')
    submit = SubmitField('Home')

class QuestionForm1(FlaskForm): #in this case only one Question form as all implemented questions are yes/no questions
    option = RadioField('select', choices=['YES', 'NO'])
    submit = SubmitField('next') #if users can chose from multiple answer options a new form would include a SelectField

class NewArticle(FlaskForm):
    url_field = StringField('Paste URL', validators=[DataRequired()])
    title = StringField('Title (optional)') #optional = no DataRequired()
    submit = SubmitField('Start analysis')

class BookmarkForm(FlaskForm):
    bookmark = BooleanField('Bookmark')
    submit = SubmitField('Bookmark')
