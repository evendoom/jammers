import os
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import (
    generate_password_hash,
    check_password_hash)
from datetime import datetime

if os.path.exists('env.py'):
    import env


app = Flask(__name__)
app.config['MONGO_DBNAME'] = os.environ.get('MONGO_DBNAME')
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
app.secret_key = os.environ.get('SECRET_KEY')
mongo = PyMongo(app)


# Intro Page
@app.route('/')
def main():
    return render_template('intro.html')


# Intro Page Search function
@app.route('/search', methods=['GET', 'POST'])
def intro_search():
    search_results = mongo.db.users.find({'username': request.form.get('search_query')})
    return render_template('intro_search.html', search_results=search_results)


# View Profile
@app.route('/search/<user_id>')
def view_profile(user_id):
    profile = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    return render_template('view_profile.html', profile=profile)


# Register Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Check if username already exists
        username_exists = mongo.db.users.find_one({'username': request.form.get('username')})

        if username_exists:
            flash('Username already exists', 'error')
            return redirect(url_for('register'))

        # Create list with instruments that have been selected 
        instruments = request.form.getlist('instrument')

        # Check if other instruments are available and add them to instruments
        if (request.form.get('other_instrument')):
            instruments.append(request.form.get('other_instrument'))
        
        # Check if user uploaded a picture
        profile_pic = None
        if 'profile_pic' in request.files:
            profile_pic = request.files['profile_pic']
            profile_pic_name = f"{request.form.get('username')}{profile_pic.filename}"
            mongo.save_file(profile_pic_name, profile_pic)
        
        # Create dictionary to send to Mongo DB
        register = {
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'username': request.form.get('username'),
            'password': generate_password_hash(request.form.get('password'), method='pbkdf2:sha256', salt_length=16),
            'city': request.form.get('city').lower(),
            'country': request.form.get('country').lower(),
            'profile_pic': profile_pic_name,
            'instruments': instruments,
            'about': request.form.get('about_yourself')
        }

        # Insert record on Mongo DB
        mongo.db.users.insert_one(register)

        # Direct user to dashboard:
        session['user'] = request.form.get('username')
        flash(f"Welcome to Jammers {register['first_name']}!", 'welcome')
        return redirect(url_for('user', username=session['user']))

    return render_template('register.html')


# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        # Check if user exists
        user_exists = mongo.db.users.find_one({'username': request.form.get('username')})

        # Check is password matches
        if user_exists:
            if check_password_hash(
                user_exists['password'], request.form.get('password')):
                # Create session user 
                session['user'] = request.form.get('username')
                return redirect(url_for('user', username=session['user']))
            else:
                flash('Invalid username / password', 'error')
                return redirect(url_for('login'))
        else:
            flash('Invalid username / password', 'error')
            return redirect(url_for('login'))
            
    return render_template('login.html')


# Terminate user session
@app.route('/logout')
def logout():
    session.pop('user')
    return redirect(url_for('main'))


# Get profile pic
@app.route('/file/<filename>')
def get_profile_pic(filename):
    return mongo.send_file(filename)


# User dashboard
@app.route('/<username>')
def user(username):
    user = mongo.db.users.find_one({'username': username})
    if session['user'] == user['username']:
        return render_template('profile_main.html', user=user)


# Dashboard Search
@app.route('/<username>/search', methods=['GET', 'POST'])
def dashboard_search(username):
    user = mongo.db.users.find_one({'username': username})
    search_results = mongo.db.users.find({'username': request.form.get('search_query')})
    return render_template('dashboard_search.html', user=user, search_results=search_results)


# Dashboard Search View Profile
@app.route('/<username>/search/<profile_id>')
def dashboard_view_user(username, profile_id):
    user = mongo.db.users.find_one({'username': username})
    profile = mongo.db.users.find_one({'_id': ObjectId(profile_id)})
    return render_template('dashboard_view_user.html', user=user, profile=profile)


# Send message to user
@app.route('/<username>/search/<profile_id>/sendMessage', methods=['GET', 'POST'])
def send_message(username, profile_id):
    from_user = mongo.db.users.find_one({'username': username})
    to_user = mongo.db.users.find_one({'_id': ObjectId(profile_id)})

    # Create dictionary to store on DB
    now = datetime.now()
    send_message = {
        'to_user': to_user['username'],
        'from_user': from_user['username'],
        'to_user_image': to_user['profile_pic'],
        'from_user_image': from_user['profile_pic'],
        'message_list': [{
            'date': now.strftime('%d/%m/%Y %H:%M'),
            'user': from_user['username'],
            'message': request.form.get('sendMessage')
        }],
        'is_new': True
    }

    # Insert record on Mongo DB
    mongo.db.messages.insert_one(send_message)

    # Redirect to user profile
    flash('Message sent!', 'welcome')
    return render_template('dashboard_view_user.html', user=from_user, profile=to_user)


# Get user messages
@app.route('/<username>/messages')
def get_messages(username):
    user = mongo.db.users.find_one({'username': username})
    messages = mongo.db.messages.find({'to_user': username})
    return render_template('messages.html', user=user, messages=messages)


# View message
@app.route('/<username>/messages/<message_id>', methods=['GET', 'POST'])
def view_message(username, message_id):
    if request.method == 'POST':
        # Get message date
        now = datetime.now()

        # Create dictionary to store on DB
        submit = {
            'date': now.strftime('%d/%m/%Y %H:%M'),
            'user': username,
            'message': request.form.get('send_message')
        }

        # Push to Mongo DB
        mongo.db.messages.update({'_id': ObjectId(message_id)}, { '$push': {'message_list': submit}})

        return redirect(url_for('get_messages', username=username))

    user = mongo.db.users.find_one({'username': username})
    messages = mongo.db.messages.find_one({'_id': ObjectId(message_id)})
    return render_template('view_message.html', user=user, messages=messages)


# View logged user's profile
@app.route('/<username>/profile')
def user_profile(username):
    user = mongo.db.users.find_one({'username': username})
    return render_template('view_user_profile.html', user=user)


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')))
