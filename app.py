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
    if 'user' in session:
        return redirect(url_for('user_dashboard'))
    else:
        return render_template('intro.html')


# Intro Page Search function
@app.route('/search', methods=['GET', 'POST'])
def intro_search():
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        search_query_lst = []
        search_results = []

        # Put multiple search query words into a list
        if ', ' in search_query:
            search_query_lst = list(search_query.split(', '))
        elif ',' in search_query:
            search_query_lst = list(search_query.split(','))
        elif ' ' in search_query:
            search_query_lst = list(search_query.split(' '))

        try:
            # Find usernames that partially
            # match search query (case insensitive)
            if search_query_lst:
                for word in search_query_lst:
                    search = mongo.db.users.find(
                        {'username':
                            {'$regex': f'.*{word}.*', '$options': 'i'}})

                    for item in search:
                        if item not in search_results:
                            search_results.append(item)
            else:
                search = mongo.db.users.find(
                    {'username':
                        {'$regex': f'.*{search_query}.*', '$options': 'i'}})

                for item in search:
                    if item not in search_results:
                        search_results.append(item)

            # Find cities or countries that match search query
            search = mongo.db.users.find({'$text': {'$search': search_query}})
            for item in search:
                if item not in search_results:
                    search_results.append(item)

            # Find instruments that match search query
            if search_query_lst:
                for word in search_query_lst:
                    search = mongo.db.users.find(
                        {'instruments':
                            {'$regex': f'.*{word}.*', '$options': 'i'}})

                    for item in search:
                        if item not in search_results:
                            search_results.append(item)
            else:
                search = mongo.db.users.find(
                    {'instruments':
                        {'$regex': f'.*{search_query}.*', '$options': 'i'}})

                for item in search:
                    if item not in search_results:
                        search_results.append(item)
        except:
            render_error()
            return render_template('intro.html')
        else:
            # Render template
            if len(search_results) == 0:
                flash('No results found.', 'info')
                return render_template('intro_search.html')
            else:
                return render_template(
                    'intro_search.html', search_results=search_results)

    return redirect(url_for('main'))


# View Profile
@app.route('/search/<user_id>')
def view_profile(user_id):
    try:
        profile = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    except:
        render_error()
        return render_template('intro.html')
    else:
        return render_template('view_profile.html', profile=profile)


# Register Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Check if username already exists
        username_exists = mongo.db.users.find_one(
            {'username': request.form.get('username')})

        if username_exists:
            flash('Username already exists', 'error')
            return redirect(url_for('register'))

        # Create a list of instruments
        instruments = request.form.getlist('instrument')

        # Check if other instruments are available
        # and add them to instruments list
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
            if profile_pic.filename == '':
                profile_pic_name = 'generic_profile_pic.jpg'
            else:
                profile_pic_name = (
                    f"{request.form.get('username')}{profile_pic.filename}")

                mongo.save_file(profile_pic_name, profile_pic)

        # Create dictionaries to send to Mongo DB
        register = {
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'username': request.form.get('username'),
            'password': generate_password_hash(request.form.get('password'),
                                               method='pbkdf2:sha256',
                                               salt_length=16),
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

        try:
            # Insert records on Mongo DB
            mongo.db.users.insert_one(register)
            mongo.db.collaborators.insert_one(collaborations)
        except:
            render_error()
            return render_template('intro.html')
        else:
            # Direct user to dashboard:
            session['user'] = request.form.get('username')
            flash(f"Welcome to Jammers {register['first_name']}!", 'info')
            return redirect(url_for('user_dashboard'))

    return render_template('register.html')


# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        try:
            # Check if user exists
            user_exists = mongo.db.users.find_one(
                {'username': request.form.get('username')})
        except:
            render_error()
            return render_template('intro.html')
        else:
            # Check is password matches
            if user_exists:
                if check_password_hash(user_exists['password'],
                                       request.form.get('password')):

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
    try:
        user = mongo.db.users.find_one({'username': session['user']})
        new_messages = check_new_messages()
    except:
        render_error()
        return render_template('intro.html')
    else:
        return render_template(
            'profile_main.html', user=user, new_messages=new_messages)


# Dashboard Search
@app.route('/dashboard/search', methods=['GET', 'POST'])
def dashboard_search():
    if request.method == 'POST':
        user = mongo.db.users.find_one({'username': session['user']})
        new_messages = check_new_messages()
        search_query = request.form.get('search_query')
        search_query_lst = []
        search_results = []

        # Put search query words into a list
        if ', ' in search_query:
            search_query_lst = list(search_query.split(', '))
        elif ',' in search_query:
            search_query_lst = list(search_query.split(','))
        elif ' ' in search_query:
            search_query_lst = list(search_query.split(' '))

        try:
            # Find usernames that partially
            # match search query (case insensitive)
            if search_query_lst:
                for word in search_query_lst:
                    search = mongo.db.users.find(
                        {'username':
                            {'$regex': f'.*{word}.*', '$options': 'i'}})
                    for item in search:
                        if item not in search_results:
                            search_results.append(item)
            else:
                search = mongo.db.users.find(
                    {'username':
                        {'$regex': f'.*{search_query}.*', '$options': 'i'}})
                for item in search:
                    if item not in search_results:
                        search_results.append(item)

            # Find cities or countries that match search query
            search = mongo.db.users.find({'$text': {'$search': search_query}})
            for item in search:
                if item not in search_results:
                    search_results.append(item)

            # Find instruments that match search query
            if search_query_lst:
                for word in search_query_lst:
                    search = mongo.db.users.find(
                        {'instruments':
                            {'$regex': f'.*{word}.*', '$options': 'i'}})
                    for item in search:
                        if item not in search_results:
                            search_results.append(item)
            else:
                search = mongo.db.users.find(
                    {'instruments':
                        {'$regex': f'.*{search_query}.*', '$options': 'i'}})
                for item in search:
                    if item not in search_results:
                        search_results.append(item)
        except:
            render_error()
            return render_template('intro.html')
        else:
            # Render template
            if len(search_results) == 0:
                flash('No results found.', 'info')
                return render_template(
                    'dashboard_search.html',
                    user=user,
                    new_messages=new_messages)
            else:
                return render_template(
                    'dashboard_search.html',
                    user=user,
                    search_results=search_results,
                    new_messages=new_messages)

    return redirect(url_for('user_dashboard'))


# Dashboard Search View Profile
@app.route('/dashboard/search/<profile_id>')
def dashboard_view_user(profile_id):
    try:
        user = mongo.db.users.find_one({'username': session['user']})
        new_messages = check_new_messages()
        profile = mongo.db.users.find_one({'_id': ObjectId(profile_id)})
        collaborators = mongo.db.collaborators.find_one(
            {'user': session['user']})
    except:
        render_error()
        return render_template('intro.html')
    else:
        return render_template('dashboard_view_user.html',
                               user=user, profile=profile,
                               collaborators=collaborators,
                               new_messages=new_messages)


# Send message to user
@app.route('/dashboard/search/<profile_id>/sendMessage',
           methods=['GET', 'POST'])
def send_message(profile_id):
    if request.method == 'POST':
        try:
            from_user = mongo.db.users.find_one({'username': session['user']})
            to_user = mongo.db.users.find_one({'_id': ObjectId(profile_id)})

            # Create dictionary to store on DB
            now = datetime.now()
            send_message = {
                'date_created': now.strftime('%d/%m/%Y %H:%M'),
                'to_user': to_user['username'],
                'from_user': from_user['username'],
                'to_user_image': to_user['profile_pic'],
                'from_user_image': from_user['profile_pic'],
                'message_list': [{
                    'date': now.strftime('%d/%m/%Y %H:%M'),
                    'user': from_user['username'],
                    'message': request.form.get('sendMessage')
                }],
                'latest_message': request.form.get('sendMessage'),
                'is_new': True,
                'is_archived': False,
                'related_message_id': False
            }

            # Insert record on Mongo DB
            mongo.db.messages.insert_one(send_message)
        except:
            render_error()
            return render_template('intro.html')
        else:
            # Redirect to user profile
            flash('Message sent!', 'info')
            return redirect(
                url_for('dashboard_view_user', profile_id=profile_id))

    return redirect(url_for('user_dashboard'))


# Post feedback on user profile page
@app.route('/dashboard/search/<profile_id>/postFeedback',
           methods=['GET', 'POST'])
def post_feedback(profile_id):
    if request.method == 'POST':
        try:
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
            mongo.db.users.update_one(
                {'_id': ObjectId(profile_id)},
                {'$push': {'feedback': feedback}})
        except:
            render_error()
            return render_template('intro.html')
        else:
            # Redirect to user profile
            flash('Feedback posted!', 'info')
            return redirect(
                url_for('dashboard_view_user', profile_id=profile_id))

    return redirect(url_for('user_dashboard'))


# Add collaborator
@app.route('/dashboard/search/<profile_id>/addCollaborator')
def add_collaborator(profile_id):
    try:
        collaborator = mongo.db.users.find_one({'_id': ObjectId(profile_id)})

        # Push collaboration to user's collaborators collection
        mongo.db.collaborators.update_one(
            {'user': session['user']},
            {'$push': {'collaborations': collaborator['username']}})

    except:
        render_error()
        return render_template('intro.html')
    else:
        # Redirect to user profile
        flash('User added!', 'info')
        return redirect(url_for('dashboard_view_user', profile_id=profile_id))


# Remove collaborator
@app.route('/dashboard/search/<profile_id>/removeCollaborator')
def remove_collaborator(profile_id):
    try:
        collaborator = mongo.db.users.find_one({'_id': ObjectId(profile_id)})

        # Remove collaboration from user's collaborators collection
        mongo.db.collaborators.update_one(
            {'user': session['user']},
            {'$pull': {'collaborations': collaborator['username']}})

    except:
        render_error()
        return render_template('intro.html')
    else:
        # Redirect to user profile
        flash('User removed!', 'info')
        return redirect(url_for('dashboard_view_user', profile_id=profile_id))


# View collaborations
@app.route('/dashboard/collaborators')
def view_collaborators():
    try:
        user = mongo.db.users.find_one({'username': session['user']})
        new_messages = check_new_messages()

        # Get all members from user's collaborators collection
        collabs_db = mongo.db.collaborators.find_one(
            {'user': session['user']})['collaborations']

        # Create an empty list that will store all members' details
        collabs = []

        # Iterate through all members in collaborators collection
        # and add their details to collabs
        for collab in collabs_db:
            details = mongo.db.users.find_one({'username': collab})
            collabs.append(details)
    except:
        render_error()
        return render_template('intro.html')
    else:
        # Render template
        if len(collabs) == 0:
            flash('You have 0 collaborators. Search and add users!',
                  'info')
            return render_template(
                'collaborators.html',
                user=user,
                new_messages=new_messages)
        else:
            return render_template(
                'collaborators.html',
                user=user,
                collabs=collabs,
                new_messages=new_messages)


# Get user messages
@app.route('/dashboard/messages')
def get_messages():
    try:
        user = mongo.db.users.find_one({'username': session['user']})

        messages = list(mongo.db.messages.find(
            {'to_user': session['user'], 'is_archived': False}))

        messages = sorted(messages, key=lambda
                          k: (k['is_new'], datetime.strptime(k['date_created'],
                              '%d/%m/%Y %H:%M')),
                          reverse=True)

        # Check new messages
        new_messages = check_new_messages()
    except:
        render_error()
        return render_template('intro.html')
    else:
        if len(messages) == 0:
            flash('You have 0 messages', 'info')
            return render_template('messages.html',
                                   user=user,
                                   new_messages=new_messages)
        else:
            return render_template('messages.html',
                                   user=user,
                                   messages=messages,
                                   new_messages=new_messages)


# View message
@app.route('/dashboard/messages/<message_id>', methods=['GET', 'POST'])
def view_message(message_id):
    if request.method == 'POST':
        try:
            # Get message date
            now = datetime.now()

            # Create dictionary to update message_list
            submit = {
                'date': now.strftime('%d/%m/%Y %H:%M'),
                'user': session['user'],
                'message': request.form.get('send_message')
            }

            # Push to Mongo DB
            mongo.db.messages.update_one(
                {'_id': ObjectId(message_id)},
                {'$push': {'message_list': submit}})

            # Create dictionary for reply
            msg = mongo.db.messages.find_one({'_id': ObjectId(message_id)})

            if not msg['related_message_id']:

                reply = {
                    'date_created': now.strftime('%d/%m/%Y %H:%M'),
                    'to_user': msg['from_user'],
                    'from_user': msg['to_user'],
                    'to_user_image': msg['from_user_image'],
                    'from_user_image': msg['to_user_image'],
                    'message_list': msg['message_list'],
                    'latest_message': request.form.get('send_message'),
                    'is_new': True,
                    'is_archived': False,
                    'related_message_id': msg['_id'],
                }

                # Push to Mongo DB
                mongo.db.messages.insert_one(reply)

                # Update 'related_message_id' of original message
                reply = mongo.db.messages.find_one(
                    {'related_message_id': ObjectId(message_id)})

                mongo.db.messages.update_one(
                    {'_id': ObjectId(message_id)},
                    {'$set': {'related_message_id': reply['_id']}})

            else:
                mongo.db.messages.update_many(
                    {'related_message_id': ObjectId(message_id)},
                    {'$set': {
                        'date_created': now.strftime('%d/%m/%Y %H:%M'),
                        'latest_message': request.form.get('send_message'),
                        'is_new': True}},
                    upsert=True)

                mongo.db.messages.update_one(
                    {'related_message_id': ObjectId(message_id)},
                    {'$push': {'message_list': submit}})

        except:
            render_error()
            return render_template('intro.html')
        else:
            flash('Message Sent!', 'info')
            return redirect(url_for('get_messages'))

    try:
        user = mongo.db.users.find_one({'username': session['user']})
        message = mongo.db.messages.find_one({'_id': ObjectId(message_id)})

        # Update message status
        message_status = message['is_new']
        if message_status:
            mongo.db.messages.update_one(
                {'_id': ObjectId(message_id)},
                {'$set': {'is_new': False}})

        new_messages = check_new_messages()
    except:
        render_error()
        return render_template('intro.html')
    else:
        return render_template('view_message.html',
                               user=user,
                               message=message,
                               new_messages=new_messages)


# Archive Messages
@app.route('/dashboard/messages/archive/<message_id>')
def archive_message(message_id):
    try:
        # Update message 'is_new' status
        if mongo.db.messages.find_one({'_id': ObjectId(message_id)})['is_new']:
            mongo.db.messages.update_one(
                {'_id': ObjectId(message_id)},
                {'$set': {'is_new': False}})

        # Update message 'is_archived' status
        mongo.db.messages.update_one(
            {'_id': ObjectId(message_id)},
            {'$set': {'is_archived': True}})

    except:
        render_error()
        return render_template('intro.html')

    else:
        # Redirect user to get_messages()
        flash('Message archived!', 'info')
        return redirect(url_for('get_messages'))


# Unarchive Messages
@app.route('/dashboard/messages/view_archived/unarchive/<archive_id>')
def unarchive_message(archive_id):
    try:
        mongo.db.messages.update_one(
            {'_id': ObjectId(archive_id)},
            {'$set': {'is_archived': False}})

    except:
        render_error()
        return render_template('intro.html')

    else:
        # Redirect user to get_messages()
        flash('Message unarchived!', 'info')
        return redirect(url_for('get_messages'))


# Delete Messages
@app.route('/dashboard/messages/view_archived/delete/<archive_id>')
def delete_message(archive_id):
    try:
        mongo.db.messages.delete_one({'_id': ObjectId(archive_id)})

        mongo.db.messages.update_one(
            {'related_message_id': ObjectId(archive_id)},
            {'$set': {'related_message_id': False}})

    except:
        render_error()
        return render_template('intro.html')
    else:
        # Redirect user to get_messages()
        flash('Message deleted!', 'info')
        return redirect(url_for('get_messages'))


# View archived messages
@app.route('/dashboard/messages/view_archived')
def view_archived():
    try:
        user = mongo.db.users.find_one({'username': session['user']})
        new_messages = check_new_messages()
        archived = list(mongo.db.messages.find(
            {'to_user': session['user'], 'is_archived': True}))
        archived = sorted(archived, key=lambda
                          k: (datetime.strptime
                              (k['date_created'], '%d/%m/%Y %H:%M')),
                          reverse=True)
    except:
        render_error()
        return render_template('intro.html')
    else:
        if len(archived) == 0:
            flash('No archived messages!', 'info')
            return render_template(
                'view_archived_messages.html',
                user=user,
                new_messages=new_messages)
        else:
            return render_template(
                'view_archived_messages.html',
                user=user,
                archived=archived,
                new_messages=new_messages)


# View logged user's profile
@app.route('/dashboard/profile')
def user_profile():
    try:
        user = mongo.db.users.find_one({'username': session['user']})
        new_messages = check_new_messages()
    except:
        render_error()
        return render_template('intro.html')
    else:
        return render_template(
            'view_user_profile.html',
            user=user,
            new_messages=new_messages)


# Edit profile
@app.route('/dashboard/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    try:
        user = mongo.db.users.find_one({'username': session['user']})
        new_messages = check_new_messages()
    except:
        render_error()
        return render_template('intro.html')
    else:
        if request.method == 'POST':
            # Create list with instruments that have been selected
            instruments = request.form.getlist('instrument')

            # Check if other instruments are available
            # and add them to instruments list
            if request.form.get('other_instrument'):
                other_instruments_str = request.form.get('other_instrument')
                if ', ' in other_instruments_str:
                    other_instruments_lst = list(
                        other_instruments_str.split(', '))
                    for item in other_instruments_lst:
                        instruments.append(item.lower())
                elif ',' in other_instruments_str:
                    other_instruments_lst = list(
                        other_instruments_str.split(','))
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
                    profile_pic_name = (
                        f"{user['username']}{profile_pic.filename}")
                    mongo.save_file(profile_pic_name, profile_pic)

                    # Delete user's old profile pic
                    if user['profile_pic'] != 'generic_profile_pic.jpg':
                        file_id = mongo.db.fs.files.find_one(
                            {'filename': user['profile_pic']})['_id']
                        mongo.db.fs.files.delete_one(
                            {'filename': user['profile_pic']})
                        mongo.db.fs.chunks.delete_one(
                            {'files_id': ObjectId(file_id)})

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

            try:
                # Update user on Mongo DB
                # Update 'users' collection
                mongo.db.users.update_one(
                    {'_id': ObjectId(user['_id'])},
                    {'$set': update_profile})
                # Update 'messages' collection
                mongo.db.messages.update_many(
                    {'to_user': user['username']},
                    {'$set': {'to_user_image': profile_pic_name}})
                mongo.db.messages.update_many(
                    {'from_user': user['username']},
                    {'$set': {'from_user_image': profile_pic_name}})
            except:
                render_error()
                return render_template('intro.html')
            else:
                # Redirect user to profile page
                flash('Profile updated!', 'info')
                return redirect(url_for('user_profile'))

        # Separate instruments that have an HTML checkbox
        # from the 'Other instruments' input HTML field
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

        return render_template(
            'edit_profile.html',
            user=user,
            other_instruments=other_instruments,
            new_messages=new_messages)


# Delete user profile
@app.route('/dashboard/profile/delete')
def delete_profile():
    try:
        user = mongo.db.users.find_one({'username': session['user']})

        # Delete user from 'users' collection
        mongo.db.users.delete_one({'username': user['username']})

        # Delete user's 'collaborators' collection
        mongo.db.collaborators.delete_one({'user': user['username']})

        # Delete messages related to user
        mongo.db.messages.delete_many(
            {'$or': [
                {'to_user': user['username']},
                {'from_user': user['username']}
                ]})

        # Delete user from other users' 'collaborators' collection
        mongo.db.collaborators.update_many(
            {'collaborations': user['username']},
            {'$pull': {'collaborations': user['username']}})

        # Delete profile picture from DB
        if user['profile_pic'] != 'generic_profile_pic.jpg':
            file_id = mongo.db.fs.files.find_one(
                {'filename': user['profile_pic']})['_id']
            mongo.db.fs.files.delete_one(
                {'filename': user['profile_pic']})
            mongo.db.fs.chunks.delete_one({'files_id': ObjectId(file_id)})
    except:
        render_error()
        return render_template('intro.html')
    else:
        # Terminate user session and redirect to main page
        session.pop('user')
        flash('Profile deleted!', 'info')
        return redirect(url_for('main'))


# About page
@app.route('/about')
def about():
    try:
        if 'user' in session:
            user = mongo.db.users.find_one({'username': session['user']})
            return render_template('about.html', user=user)
        else:
            return render_template('about.html')
    except:
        render_error()
        return render_template('intro.html')


# 404 error handler
@app.errorhandler(404)
def not_found(e):
    flash('Ooops, page does not exist!', 'error')
    return redirect(url_for('main'))


# Check new messages
def check_new_messages():
    messages = list(mongo.db.messages.find({'to_user': session['user']}))
    new_messages = 0

    for message in messages:
        if message['is_new']:
            new_messages = new_messages + 1

    return new_messages


# Flash message and kill user for except blocks:
def render_error():
    flash('Internal error, please try again later!', 'error')

    if 'user' in session:
        session.pop('user')


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')))
