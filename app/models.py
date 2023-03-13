#file that is responsible for the abstract layout of the tables
#structure of the table calles users
from app import db
#defining properties of the database
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from hashlib import md5

followers = db.Table('followers',
db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
db.Column('followed_id', db.Integer, db.ForeignKey('user.id')))

class User(UserMixin, db.Model):
    #defining the columns
    id = db.Column(db.Integer, primary_key = True) #parameter takes datatype, primary_key is the key that identifies this row uniquely
    username = db.Column(db.String(64), index = True, unique = True) #unique parametre says there is only unique user names like instagram
    email = db.Column(db.String(64), index = True, unique = True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    scored = db.relationship('History', backref='person', lazy='dynamic')
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship('User', secondary=followers, #links User instances to other User instances
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic') #dynamic: query only runs when specifically requested
    liked = db.relationship('PostLike',
        foreign_keys='PostLike.user_id',
        backref='user', lazy='dynamic')

    def __repr__(self): #because we want the info itself not just the memoryadress
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size) #avatar is randomly generated using gravatar

    def follow(self, user): #could be treated like a list with append but making a functionality of the User class
        if not self.is_following(user): #checking if current user already follows user
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user): #querying
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0 #returns either 0 or 1 so >0 is the same

    def followed_posts(self):
        followed = Post.query.join( followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc()) #joins own posts with followed posts for 'home feed'

    def followed_posts(self):
        followed = Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())
        #above query joins the table followers with the posts and corresponding user_ids
        #then filtered to only see the ones that a logged in user is following
        #lastly sorted by descendign date
    def like_post(self, post):
        if not self.has_liked_post(post):
            like = PostLike(user_id=self.id, post_id=post.id)
            db.session.add(like)

    def unlike_post(self, post):
        if self.has_liked_post(post):
            PostLike.query.filter_by(
                user_id=self.id,
                post_id=post.id).delete() #removes entry for the like

    def has_liked_post(self, post):
        return PostLike.query.filter(
            PostLike.user_id == self.id,
            PostLike.post_id == post.id).count() > 0 #checks if entry for liker and liked post exists

class PostLike(db.Model):
    __tablename__ = 'post_like'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))



@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    likes = db.relationship('PostLike', backref='post', lazy='dynamic')

    def __repr__(self): #because we want the info itself not just the memoryadress
        return '<Post {}>'.format(self.body)

class History(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    url = db.Column(db.String(120))
    title = db.Column(db.String(140))
    score = db.Column(db.Integer)
    bookmark = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<History {}>'.format(self.score)



class Questions(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    sub = db.Column(db.Integer)
    content = db.Column(db.String(140))
    yes_points = db.Column(db.Integer)
    no_points = db.Column(db.Integer)
    opt_points = db.Column(db.Integer)

    def __repr__(self):
        return 'Question: {}'.format(self.content)




class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    score_min = db.Column(db.Integer)
    score_max = db.Column(db.Integer)
    title = db.Column(db.String(64))
    text = db.Column(db.String(500))
    def __repr__(self):
        return '<Feedback {}>'.format(self.score_min)
