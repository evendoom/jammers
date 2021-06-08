import os
from flask import (
    Flask, render_template, request)
from flask_pymongo import PyMongo
from werkzeug.security import (
    generate_password_hash,
    check_password_hash)

if os.path.exists('env.py'):
    import env

app = Flask(__name__)
app.config['MONGO_DBNAME'] = os.environ.get('MONGO_DBNAME')
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
app.secret_key = os.environ.get('SECRET_KEY')
mongo = PyMongo(app)

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=os.environ.get('PORT'))


@app.route('/')
def main():
    return render_template('intro.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Create list with instruments that have been selected 
        instruments = request.form.getlist('instrument')

        # Check if other instruments are available and add them to check_inst
        if (request.form.get('other_instrument')):
            instruments.append(request.form.get('other_instrument'))
        
        register = {
            'first_name': request.form.get('first_name').lower(),
            'last_name': request.form.get('last_name').lower(),
            'username': request.form.get('username'),
            'password': generate_password_hash(request.form.get('password'), method='pbkdf2:sha256', salt_length=16),
            'instruments': instruments,
            'about': request.form.get('about_yourself')
        }

        print(register)
        
    return render_template('register.html')


@app.route('/login')
def login():
    return render_template('login.html')