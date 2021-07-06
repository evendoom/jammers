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
    search_query = request.form.get('search_query')
    search_results = []

    # Find usernames that partially match search query (case insensitive)
    search = mongo.db.users.find({ 'username': { '$regex': f'.*{search_query}.*', '$options': 'i' } })
    for item in search:
        search_results.append(item)
    
    # Find cities or countries that match search query
    search = mongo.db.users.find({ '$text': { '$search': search_query } })
    for item in search:
        if item not in search_results:
            search_results.append(item)
    
    # Find instruments that match search query
    search = mongo.db.users.find({ 'instruments': { '$regex': f'.*{search_query}.*', '$options': 'i' } })
    for item in search:
        if item not in search_results:
            search_results.append(item)

    # Render template
    if len(search_results) == 0:
        flash('No results found. Hit main logo to perform another search', 'info')
        return render_template('intro_search.html')
    else:
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

        # Create a list of instruments 
        instruments = request.form.getlist('instrument')

        # Check if other instruments are available and add them to instruments list
        if request.form.get('other_instrument'):
            other_instruments_str = request.form.get('other_instrument')
            if ', ' in other_instruments_str:
                other_instruments_lst = list(other_instruments_str.split(', '))
                for item in other_instruments_lst:
                    instruments.append(item.lower())
            elif ',' in other_instruments_str:
                other_instruments_lst = list(other_instruments_str.split(','))
                for item in other_instruments_lst:
                    instruments.append(item.lower())
            else:
                instruments.append(other_instruments_str.lower())
        
        # Prevent registration if there are no instruments
        if len(instruments) == 0:
            flash('Please select an instrument!', 'error')
            return redirect(url_for('register'))

        # Check if user uploaded a picture
        if 'profile_pic' in request.files:
            profile_pic = request.files['profile_pic']
            profile_pic_name = f"{request.form.get('username')}{profile_pic.filename}"
            mongo.save_file(profile_pic_name, profile_pic)
        
        # Create dictionaries to send to Mongo DB
        register = {
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'username': request.form.get('username'),
            'password': generate_password_hash(request.form.get('password'), method='pbkdf2:sha256', salt_length=16),
            'city': request.form.get('city').lower(),
            'country': request.form.get('country').lower(),
            'profile_pic': profile_pic_name,
            'instruments': instruments,
            'about': request.form.get('about_yourself'),
            'feedback': []
        }

        collaborations = {
            'user': request.form.get('username'),
            'collaborations': []
        }

        # Insert records on Mongo DB
        mongo.db.users.insert_one(register)
        mongo.db.collaborators.insert_one(collaborations)

        # Direct user to dashboard:
        session['user'] = request.form.get('username')
        flash(f"Welcome to Jammers {register['first_name']}!", 'info')
        return redirect(url_for('user_dashboard'))

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
                return redirect(url_for('user_dashboard'))
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
@app.route('/dashboard')
def user_dashboard(): 
    user = mongo.db.users.find_one({'username': session['user']})
    new_messages = check_new_messages()
    return render_template('profile_main.html', user=user, new_messages=new_messages)


# Dashboard Search
@app.route('/dashboard/search', methods=['GET', 'POST'])
def dashboard_search():
    user = mongo.db.users.find_one({'username': session['user']})
    new_messages = check_new_messages()
    search_query = request.form.get('search_query')
    search_results = []

    # Find usernames that partially match search query (case insensitive)
    search = mongo.db.users.find({ 'username': { '$regex': f'.*{search_query}.*', '$options': 'i' } })
    for item in search:
        search_results.append(item)
    
    # Find cities or countries that match search query
    search = mongo.db.users.find({ '$text': { '$search': search_query } })
    for item in search:
        if item not in search_results:
            search_results.append(item)
    
    # Find instruments that match search query
    search = mongo.db.users.find({ 'instruments': { '$regex': f'.*{search_query}.*', '$options': 'i' } })
    for item in search:
        if item not in search_results:
            search_results.append(item)

    # Render template
    if len(search_results) == 0:
        flash('No results found. Hit main logo to perform another search', 'info')
        return render_template('dashboard_search.html', user=user, new_messages=new_messages)
    else:
        return render_template('dashboard_search.html', user=user, search_results=search_results, new_messages=new_messages)


# Dashboard Search View Profile
@app.route('/dashboard/search/<profile_id>')
def dashboard_view_user(profile_id):
    user = mongo.db.users.find_one({'username': session['user']})
    new_messages = check_new_messages()
    profile = mongo.db.users.find_one({'_id': ObjectId(profile_id)})
    collaborators = mongo.db.collaborators.find_one({'user': session['user']})
    return render_template('dashboard_view_user.html', user=user, profile=profile, collaborators=collaborators, new_messages=new_messages)


# Send message to user
@app.route('/dashboard/search/<profile_id>/sendMessage', methods=['GET', 'POST'])
def send_message(profile_id):
    from_user = mongo.db.users.find_one({'username': session['user']})
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
    flash('Message sent!', 'info')
    return redirect(url_for('dashboard_view_user', profile_id=profile_id))


# Post feedback on user profile page
@app.route('/dashboard/search/<profile_id>/postFeedback', methods=['GET', 'POST'])
def post_feedback(profile_id):
    from_user = mongo.db.users.find_one({'username': session['user']})

    # Create dictionary to store on Mongo DB
    now = datetime.now()

    feedback = {
        'from_user': from_user['username'],
        'from_user_img': from_user['profile_pic'],
        'date': now.strftime('%d/%m/%Y'),
        'feedback_msg': request.form.get('postFeedback')
    }

    # Push dictionary to Mongo DB
    mongo.db.users.update_one({'_id': ObjectId(profile_id)}, { '$push': {'feedback': feedback} })

    # Redirect to user profile
    flash('Feedback posted!', 'info')
    return redirect(url_for('dashboard_view_user', profile_id=profile_id))


# Add collaborator
@app.route('/dashboard/search/<profile_id>/addCollaborator')
def add_collaborator(profile_id):
    collaborator = mongo.db.users.find_one({'_id': ObjectId(profile_id)})

    # Push collaboration to user's collaborators collection
    mongo.db.collaborators.update_one({'user': session['user']}, { '$push': { 'collaborations': collaborator['username'] } })

    # Redirect to user profile
    flash('User added!', 'info')
    return redirect(url_for('dashboard_view_user', profile_id=profile_id))


# Remove collaborator
@app.route('/dashboard/search/<profile_id>/removeCollaborator')
def remove_collaborator(profile_id):
    collaborator = mongo.db.users.find_one({'_id': ObjectId(profile_id)})

    # Remove collaboration from user's collaborators collection
    mongo.db.collaborators.update_one({'user': session['user']}, { '$pull': { 'collaborations': collaborator['username'] } })

    # Redirect to user profile
    flash('User removed!', 'info')
    return redirect(url_for('dashboard_view_user', profile_id=profile_id))


# View collaborations
@app.route('/dashboard/collaborators')
def view_collaborators():
    user = mongo.db.users.find_one({'username': session['user']})
    new_messages = check_new_messages()

    # Get all members from user's collaborators collection
    collabs_db = mongo.db.collaborators.find_one({'user': session['user']})['collaborations']

    # Create an empty list that will store all members' details
    collabs = []

    # Iterate through all members in collaborators collection and add their details to collabs
    for collab in collabs_db:
        details = mongo.db.users.find_one({'username': collab})
        collabs.append(details)
    
    # Render template
    if len(collabs) == 0:
        flash('You have 0 collaborators. Search and add users!', 'info')
        return render_template('collaborators.html', user=user, new_messages=new_messages)
    else:
        return render_template('collaborators.html', user=user, collabs=collabs, new_messages=new_messages)


# Get user messages
@app.route('/dashboard/messages')
def get_messages():
    user = mongo.db.users.find_one({'username': session['user']})
    messages = list(mongo.db.messages.find({'to_user': session['user']}))
    messages = sorted(messages, key=lambda k: (k['is_new'], datetime.strptime(k['date_created'], '%d/%m/%Y %H:%M')), reverse=True)

    # Check new messages
    new_messages = check_new_messages()
    
    if len(messages) == 0:
        flash('You have 0 messages', 'info')
        return render_template('messages.html', user=user, new_messages=new_messages)
    else:
        return render_template('messages.html', user=user, messages=messages, new_messages=new_messages)


# View message
@app.route('/dashboard/messages/<message_id>', methods=['GET', 'POST'])
def view_message(message_id):
    if request.method == 'POST':
        # Get message date
        now = datetime.now()

        # Create dictionary to store on Mongo DB
        submit = {
            'date': now.strftime('%d/%m/%Y %H:%M'),
            'user': session['user'],
            'message': request.form.get('send_message')
        }

        # Push to Mongo DB
        mongo.db.messages.update_one({'_id': ObjectId(message_id)}, { '$push': {'message_list': submit}})

        return redirect(url_for('get_messages'))

    user = mongo.db.users.find_one({'username': session['user']})
    message = mongo.db.messages.find_one({'_id': ObjectId(message_id)})

    #Update message status
    message_status = message['is_new']
    if message_status == True:
        mongo.db.messages.update_one({'_id': ObjectId(message_id)}, { '$set': { 'is_new': False } })
    
    new_messages = check_new_messages()
    return render_template('view_message.html', user=user, message=message, new_messages=new_messages)


# View logged user's profile
@app.route('/dashboard/profile')
def user_profile():
    user = mongo.db.users.find_one({'username': session['user']})
    new_messages = check_new_messages()
    return render_template('view_user_profile.html', user=user, new_messages=new_messages)


# Edit profile
@app.route('/dashboard/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    user = mongo.db.users.find_one({'username': session['user']})
    new_messages = check_new_messages()

    if request.method == 'POST':
        # Create list with instruments that have been selected
        instruments = request.form.getlist('instrument')

        # Check if other instruments are available and add them to instruments list
        if request.form.get('other_instrument'):
            other_instruments_str = request.form.get('other_instrument')
            if ', ' in other_instruments_str:
                other_instruments_lst = list(other_instruments_str.split(', '))
                for item in other_instruments_lst:
                    instruments.append(item.lower())
            elif ',' in other_instruments_str:
                other_instruments_lst = list(other_instruments_str.split(','))
                for item in other_instruments_lst:
                    instruments.append(item.lower())
            else:
                instruments.append(other_instruments_str)

        # Prevent edit submission if there are no instruments:
        if len(instruments) == 0:
            flash('Please select an instrument!', 'error')
            return redirect(url_for('edit_profile'))

        # Check if user uploaded a picture
        if 'profile_pic' in request.files:
            profile_pic = request.files['profile_pic']
            if profile_pic.filename == '':
                profile_pic_name = user['profile_pic']
            else:
                profile_pic_name = f"{user['username']}{profile_pic.filename}"
                mongo.save_file(profile_pic_name, profile_pic)

                # Delete user's old profile pic
                file_id = mongo.db.fs.files.find_one({'filename': user['profile_pic']})['_id']
                mongo.db.fs.files.delete_one({'filename': user['profile_pic']})
                mongo.db.fs.chunks.delete_one({'files_id': ObjectId(file_id)})
        
        # Create dictionary to update Mongo DB
        update_profile = {
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'city': request.form.get('city').lower(),
            'country': request.form.get('country').lower(),
            'profile_pic': profile_pic_name,
            'instruments': instruments,
            'about': request.form.get('about_yourself')
        }

        # Update user on Mongo DB
        # Update 'users' collection
        mongo.db.users.update_one({'_id': ObjectId(user['_id'])}, { '$set': update_profile })
        # Update 'messages' collection
        mongo.db.messages.update_many({'to_user': user['username']}, { '$set': { 'to_user_image': profile_pic_name } })
        mongo.db.messages.update_many({'from_user': user['username']}, { '$set': { 'from_user_image': profile_pic_name } }) 

        # Redirect user to profile page
        flash('Profile updated!', 'info')
        return redirect(url_for('user_profile'))

    # Separate instruments that have an HTML checkbox from the 'Other instruments' input HTML field
    instrument_check = ['voice', 'guitar', 'bass', 'drums', 'keyboard']
    other_instruments_list = []

    for instrument in user['instruments']:
        if instrument not in instrument_check:
            other_instruments_list.append(instrument.capitalize())

    # Check the length of other_instruments_list
    if len(other_instruments_list) == 0:
        other_instruments = ""
    elif len(other_instruments_list) == 1:
        other_instruments = other_instruments_list[0]
    else:
        other_instruments = ", ".join(other_instruments_list)

    return render_template('edit_profile.html', user=user, other_instruments=other_instruments, new_messages=new_messages)


# Delete user profile
@app.route('/dashboard/profile/delete')
def delete_profile():
    user = mongo.db.users.find_one({'username': session['user']})
    
    # Delete user from 'users' collection
    mongo.db.users.delete_one({'username': user['username']})

    # Delete user's 'collaborators' collection
    mongo.db.collaborators.delete_one({'user': user['username']})

    # Delete messages related to user
    mongo.db.messages.delete_many({ '$or': [ { 'to_user': user['username'] }, { 'from_user': user['username'] } ] })

    # Delete profile picture from DB
    file_id = mongo.db.fs.files.find_one({'filename': user['profile_pic']})['_id']
    mongo.db.fs.files.delete_one({'filename': user['profile_pic']})
    mongo.db.fs.chunks.delete_one({'files_id': ObjectId(file_id)})

    # Terminate user session and redirect to main page
    session.pop('user')
    flash('Profile deleted!', 'info')
    return redirect(url_for('main'))
    

# Check new messages
def check_new_messages():
    messages = list(mongo.db.messages.find({'to_user': session['user']}))
    new_messages = 0

    for message in messages:
        if message['is_new']:
            new_messages = new_messages + 1
    
    return new_messages


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')))
