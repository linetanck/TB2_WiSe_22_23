from flask import render_template, flash, redirect, url_for, request
from app import App, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from app.forms import QuestionForm1, PostForm, EmptyForm, DisclaimerForm, NewArticle, BookmarkForm
from flask_login import login_user, logout_user, current_user, login_required
from app.models import User, Post, Questions, History, Feedback
from werkzeug.urls import url_parse
from datetime import datetime

@App.route('/')
@App.route('/disclaimer', methods = ['GET', 'POST'])
@login_required
def disclaimer():
    form = DisclaimerForm()
    ticked = form.checkbox.data
    if ticked == True:
        return redirect(url_for('index'))
    return render_template('disclaimer.html', title='Disclaimer', form = form)

@App.route('/index')
@login_required
def index():
    return render_template("index.html", title='Home Page')

@App.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('disclaimer')) #no need to login then
    myform = LoginForm()
    if myform.validate_on_submit():
        user = User.query.filter_by(username=myform.username.data).first()
        if user is None or not user.check_password(myform.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=myform.remember_me.data)
        return redirect(url_for('disclaimer'))
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form= myform)

@App.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('disclaimer'))

@App.route('/register', methods=['get', 'post'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index')) #no need to register then
    myform = RegistrationForm()
    if myform.validate_on_submit():
        user = User(username=myform.username.data, email=myform.email.data)
        user.set_password(myform.password.data)
        db.session.add(user)
        db.session.commit() #creates new entry in user table
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=myform)

@App.route('/user/<username>')#<> is dynamic part
@login_required
def user(username):
    form = EmptyForm()
    user = User.query.filter_by(username=username).first_or_404() #if no such user returns 404 template
    page = request.args.get('page', 1, type=int) #query string argument to specify page number
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page=page,
    per_page=App.config['POSTS_PER_PAGE'], error_out=False) #giving paginate all arguments
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None #allows us to only display next url in template if next url has a value
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
    next_url=next_url, prev_url=prev_url, form=form)

@App.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@App.route('/forum', methods = ['GET', 'POST'])
@login_required
def forum():
    myform = PostForm() #instantiates the PostForm
    if myform.validate_on_submit():
        post = Post(body=myform.post.data, author=current_user)
        db.session.add(post) #new post is added into the Post table
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('forum')) #redirect because otherwise it would repeat the POST request making UI confusing and avoid duplicates
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page=page,
    per_page=App.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('forum', page=posts.next_num) \
        if posts.has_next else None #using the pagination attributes to navigate
    prev_url = url_for('forum', page=posts.prev_num) \
        if posts.has_prev else None #next_url and prev_url are going to be set to a url specified by url_for() only if there is something there
    return render_template('forum.html', title='Home', form=myform,
    posts=posts.items, next_url=next_url, prev_url=prev_url)

@App.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=App.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('explore.html', title='Explore', posts=posts.items,
                          next_url=next_url, prev_url=prev_url)


@App.route('/questions1', methods=['GET', 'POST'])
@login_required
def questions1():
    form = QuestionForm1() #instantiates question form
    x = 0 #defines score variable as 0 to start checking
    q = Questions.query.filter_by(id = 1) #calls table entry for first question
    for i in q:
        q=i
    if form.validate_on_submit():
        if form.option.data == 'YES':
            x += q.yes_points #adds points specified for answering yes in the Questions table
        elif form.option.data =='NO':
            x += q.no_points
        points = db.session.query(History).filter(History.user_id==current_user.id).order_by(History.id.desc()).first()
        points.score = x
        db.session.add(points) #commits score to history table for now
        db.session.commit()
        return redirect(url_for('questions2'))
    return render_template('questions1.html', form = form, q = q)

@App.route('/questions2', methods=['GET', 'POST'])
@login_required
def questions2():
    y = db.session.query(History).filter(History.user_id==current_user.id).order_by(History.id.desc()).first() #queries score
    x = y.score
    form = QuestionForm1()
    q = Questions.query.filter_by(id = 2)
    for i in q:
        q=i
    if form.validate_on_submit():
        if form.option.data == 'YES':
            x += q.yes_points #adds corresponding points
            y.score = x
            db.session.add(y)
            db.session.commit()
            return redirect(url_for('questions3')) #redirects depending on quesitons' relationship to each other
        elif form.option.data == 'NO':
            x += q.no_points
            y.score = x
            db.session.add(y)
            db.session.commit()
            return redirect(url_for('questions4'))
    return render_template('questions1.html', form = form, q = q)

@App.route('/questions3', methods=['GET', 'POST'])
@login_required
def questions3():
    y = db.session.query(History).filter(History.user_id==current_user.id).order_by(History.id.desc()).first()
    x = y.score
    form = QuestionForm1()
    q = Questions.query.filter_by(id = 3)
    for i in q:
        q=i
    if form.validate_on_submit():
        if form.option.data == 'YES':
            x += q.yes_points
        elif form.option.data == 'NO':
            x += q.no_points
        print(x)
        y.score = x
        db.session.add(y)
        db.session.commit()
        return redirect(url_for('questions4'))
    return render_template('questions1.html', form = form, q = q)

@App.route('/questions4', methods=['GET', 'POST'])
@login_required
def questions4():
    y = db.session.query(History).filter(History.user_id==current_user.id).order_by(History.id.desc()).first()
    x = y.score
    form = QuestionForm1()
    q = Questions.query.filter_by(id = 4)
    for i in q:
        q=i
    if form.validate_on_submit():
        if form.option.data == 'YES':
            x += q.yes_points
            y.score = x
            db.session.add(y)
            db.session.commit()
            return redirect(url_for('questions5'))
        elif form.option.data == 'NO':
            x += q.no_points
            y.score = x
            db.session.add(y)
            db.session.commit()
            return redirect(url_for('feedback'))
    return render_template('questions1.html', form = form, q = q)

@App.route('/questions5', methods=['GET', 'POST'])
@login_required
def questions5():
    y = db.session.query(History).filter(History.user_id==current_user.id).order_by(History.id.desc()).first()
    x = y.score
    form = QuestionForm1()
    q = Questions.query.filter_by(id = 5)
    for i in q:
        q=i
    if form.validate_on_submit():
        if form.option.data == 'YES':
            x += q.yes_points
            y.score = x
            db.session.add(y)
            db.session.commit()
            return redirect(url_for('feedback'))
        elif form.option.data == 'NO':
            x += q.no_points
            y.score = x
            db.session.add(y)
            db.session.commit()
            return redirect(url_for('feedback'))
    return render_template('questions1.html', form = form, q = q)

@App.route('/feedback', methods = ['GET', 'POST'])
@login_required
def feedback():
    form = BookmarkForm()
    score = db.session.query(History).filter(History.user_id==current_user.id).order_by(History.id.desc()).first() #this query now returns the final score
    final_score = score.score
    url = score.url
    if final_score <= 12: #boundaries for the corresponding feedback
        feedback_data = Feedback.query.filter_by(id = 1)
        for i in feedback_data:
            feedback_data = i
        if form.validate_on_submit():
            print('yes')
            score = db.session.query(History).filter(History.user_id==current_user.id).order_by(History.id.desc()).first()
            score.bookmark = 1 #if user bookmarks, entry in table is changed
            db.session.add(score)
            db.session.commit()
            return redirect(url_for('bookmarked'))
        return render_template('feedback_1.html', form=form,
        final_score=final_score, feedback_data=feedback_data, url=url)
    elif (final_score >= 13) and (final_score <= 24):
        feedback_data = Feedback.query.filter_by(id = 2)
        for i in feedback_data:
            feedback_data = i
        if form.validate_on_submit():
            if form.bookmark.data:
                score.bookmark = 'y'
                db.session.add(score)
                db.session.commit()
                return redirect(url_for('bookmarked'))
        return render_template('feedback_2.html', form=form,
        final_score=final_score, feedback_data=feedback_data, url=url)
    elif (final_score >= 25 and final_score <= 36):
        feedback_data = Feedback.query.filter_by(id = 3)
        for i in feedback_data:
            feedback_data = i
        if form.validate_on_submit():
            if form.bookmark.data:
                score.bookmark = 'y'
                db.session.add(score)
                db.session.commit()
                return redirect(url_for('bookmarked'))
        return render_template('feedback_3.html', form=form,
        final_score=final_score, feedback_data=feedback_data, url=url)
    elif (final_score >= 37 and final_score <= 34):
        feedback_data = Feedback.query.filter_by(id = 4)
        for i in feedback_data:
            feedback_data = i
        if form.validate_on_submit():
            if form.bookmark.data:
                score.bookmark = 'y'
                db.session.add(score)
                db.session.commit()
                return redirect(url_for('bookmarked'))
        return render_template('feedback_4.html', form=form,
        final_score=final_score, feedback_data=feedback_data, url=url)

@App.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@App.route('/new_article', methods=['GET', 'POST'])
@login_required
def new_article():
    form = NewArticle()
    if form.validate_on_submit():
        new_article = History(url=form.url_field.data,
        title=form.title.data, person=current_user) #user gives url and optional title here
        db.session.add(new_article)
        db.session.commit()
        flash('Lets start!')
        return redirect(url_for('questions1'))
    return render_template('new_article.html', title='New Article', form=form)

@App.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('user', username=username))
        current_user.follow(user) #uses User methods specified in models
        db.session.commit()
        flash('You are following {}!'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

@App.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You are not following {}.'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

@App.route('/bookmarked', methods = ['GET', 'POST'])
@login_required
def bookmarked():
    page = request.args.get('page', 1, type=int)
    bookmarks = db.session.query(History).filter(History.user_id==current_user.id).filter_by(bookmark=1).order_by(History.id.desc()).paginate(page=page,
    per_page=App.config['ENTRIES_PER_PAGE'], error_out=False)
    next_url = url_for('bookmarked', page=bookmarks.next_num) \
        if bookmarks.has_next else None #using the pagination attributes to navigate
    prev_url = url_for('bookmarked', page=bookmarks.prev_num) \
        if bookmarks.has_prev else None #next_url and prev_url are going to be set to a url specified by url_for() only if there is something there
    return render_template('bookmark.html', title='Bookmarks',
    bookmarks=bookmarks.items, next_url=next_url, prev_url=prev_url)

@App.route('/history', methods = ['GET', 'POST'])
@login_required
def history():
    page = request.args.get('page', 1, type=int)
    bookmarks = db.session.query(History).filter(History.user_id==current_user.id).order_by(History.id.desc()).paginate(page=page,
    per_page=App.config['ENTRIES_PER_PAGE'], error_out=False)
    #only difference between history and bookmarks is the query whether bookmark=1
    next_url = url_for('history', page=bookmarks.next_num) \
        if bookmarks.has_next else None
    prev_url = url_for('history', page=bookmarks.prev_num) \
        if bookmarks.has_prev else None
    return render_template('history.html', title='History',
    bookmarks=bookmarks.items, next_url=next_url, prev_url=prev_url)


@App.route('/like/<int:post_id>/<action>') #handles liking a post but depends on action specified in template
@login_required
def like_action(post_id, action):
    post = Post.query.filter_by(id=post_id).first_or_404()
    if action == 'like':
        current_user.like_post(post)
        db.session.commit()
    if action == 'unlike':
        current_user.unlike_post(post)
        db.session.commit()
    return redirect(request.referrer)
