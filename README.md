# Jammers

Jammers is a service that allows its users to collaborate online with singer / songwriters and musicians all over the world. The word 'Jammers' is derived from the verb 'To Jam', often used by musicians when they get together and play music.

At its initial stage, the service allows users to exchange messages between each other, but its ambition is to integrate a DAW (Digital Audio Workstation) on the website, which will allow users to record, edit and mix their songs on the cloud, and have other users to collaborate on their projects.

There is currently no company / service that has successfully achieved this, thus putting Jammers in a very good market position.

## 1 UX

### 1.1 Target Audience

The target audience for this service are musicians (including singer / songwriters) that are looking for other musicians to boost their creative ideas and musical compositions. The company expects its users to be 18 years or older, and have at least basic computer skills.

### 1.2 User Stories

#### 1.2.1 First time user goals

As a first time user, I expect the following:

* Learn more about the service
* Quickly search for members that are currently using the app
* Easily create a user profile

#### 1.2.2 Frequent user goals

As a frequent user, I expect the following:

* Easily log into my dashboard
* Quickly search for other users
* Be able to contact other users and keep a record of our message exchange
* Access a database containing my favourite users
* Leave feedback on another member's page
* Edit / delete my profile
* Be able to log out

## 2. Features

This app can be split into 4 main sections:

1. Main page
2. Login page
3. Register page
4. User dashboard

A PDF containing all wireframes for main sections and subsections can be found [here](wireframes/jammers_wireframes.pdf).

Please note that the PDF document only includes wireframes for desktop and mobile design. Tablets will take the mobile design when viewed as portrait, and desktop / laptop design when viewed as landscape.

The main colours on the app are black, white and purple. I opted for dark colours, as these are less distracting to the user.

The main font on the website is 'Noto Sans JP', with a fallback on Sans Serif. 'Noto Sans JP' is an atractive, easy to read font.

### 2.1 Main page

The [main page](wireframes/main_page.png) provides the user with basic information about the service. It allows the user to register a profile, do a search on current users and also look for more information regarding the company's goals.

### 2.2 Login page

The [login page](wireframes/login_page.png) allows registered users to easily log onto their dashboard.

### 2.3 Register page

The [register page](wireframes/register.png) displays a simple, yet elegant form that allows the visitor to create a profile.

### 2.4 User Dashboard

The user dashboard allows logged-in members to check their messages, view their favourite collaborators and also edit / delete their profile. The initial dashboard page allows the user to search for other members.

Subsections of this app will be discussed on the testing section.

## 3. Technologies Used

### 3.1 Languages Used

The following languages were used on this app:

* HTML
* CSS
* Javacript
* Python

### 3.2 Frameworks / Libraries / Programs Used

The following were used on the development of this app:

* [Flask 2.0.1](https://flask.palletsprojects.com/en/2.0.x/)

    A lightweight WSGI web application framework for Python.

* [Materialize 1.0.0](https://materializecss.com/)

    A CSS responsive front-end framework.

* [JQuery 3.6.0](https://jquery.com/)

    Used in conjunction with Materialize and also to autoresize textboxes in modals.

* [Google Fonts](https://fonts.google.com)

    The app's main font ('Noto Sans JP') was taken from Google Fonts.

* [Font Awesome 5.15.3](https://fontawesome.com/)

    All icons on the website were derived from Font Awesome.

* [Freelogo Design](https://editor.freelogodesign.org/)

    Used to create the logo for the wesbite.

* [Unsplash](https://unsplash.com/)

    Background Hero Image and user profile pictures were taken from website Unsplash.

* [Balsamiq](https://balsamiq.com/)

    Used to create wireframes.

## 4. Testing

### 4.1 Code Validation

CSS, Javascript and Python validators were used to check and validate the code on each page of this app. The W3C HTML Markup validator was not used, because it does not work with HTML files containing Jinja templates.

* [HTML Validator](https://validator.w3.org/)

    Because the HTML validator doesn't recognize Jinja code, it is not possible to copy-paste the code straight into the validator, as this will result in errors.

    To work around this, I loaded each page on Firefox, right clicked on the page and selected 'View Page Source'. This will open a new window with the HTML code. I then copy-pasted that code into the validator to check for warnings / errors.

    A result example can be found [here](wireframes/html_validator.png).

* [CSS Validator](https://jigsaw.w3.org/css-validator/) - [Results](wireframes/css_validator_style_css.png)
* [JS Validator](https://jshint.com/) - Results for both JS files: [autocomplete.js](wireframes/js_validator_autocomplete_js.png) and [script.js](wireframes/js_validator_script_js.png)

    The validation for autocomplete came up with a warning regarding confusing semantics. However, the inp argument is required to get the value from the autocomplete function.
    
* [Python Validator](http://pep8online.com/) - [Results](wireframes/pep8_validation_app_py.png)

### 4.2 Manual Testing of Buttons and Links

Manually tested all buttons and links on the app, they behave as expected: trigger the correct URL and / or trigger CRUD functionalities.

All functionalities related to buttons and links are encapsulated within Python try / except blocks, so if the code fails the 'try' block, the user is sent to the main page. I tested this by doing two things:

* Purposely write faulty syntax and see how the code behaves.

    For example, on the following code:

    ```
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
    ```

    I changed the `check_new_messages()` function to `chek_new_messages()`. This causes an error, which triggers the except block, leading the user to the main page with a message stating 'Internal error, please try again later!'

* Simulate a database communication failure, by using a database collection that doesn't exist.

    Using the same code as above, I changed `mongo.db.users.find_one({'username': session['user']})` to `mongo.db.userss.find_one({'username': session['user']})`. Because the collection 'userss' doesn't exist, an error is triggered and the code within the except block runs successfully.

### 4.3 User Stories Testing

1. First time user goals

    - Learn more about the service

        - The text on the main page ('Find musicians to collaborate with your songs') explains the visitor the main purpose of the app's service.

        - The 'About' [page](wireframes/about_screenshot.png) provides the user with more information regarding Jammers' current and future goals.

    - Quickly search for members that are currently using the app

        - The search function on the intro page allows visitors to search for current members either by username, instrument or location. Search words are not exclusive, so, for example, if one types 'saxophone, london', the results page will display all users that play saxophone and all users that live in a city called London - see example [here](wireframes/search_results_screenshot.png). The visitor is also allowed to click on a member's [profile](wireframes/user_profile_screenshot.png) to view more information. The visitor cannot message or leave feedback back on a member's profile, unless the visitor is logged in.

    - Easily create a user profile

        - The visitor can click on the 'Register' page, which will lead the user to an easy to submit form.

2. Frequent user goals

    - Easily log into my dashboard

        - The user can click on the 'Login' button on the intro page. This will lead the user to a page asking for the username and password. If both fields are correct, the user can then access his dashboard.

    - Quickly search for other users

        - The main dashboard page allows the user to search for current members either by username, instrument or location. Search words are not exclusive, so, for example, if one types 'saxophone, london', the results page will display all users that play saxophone and all users that live in a city called London - see example [here](wireframes/dashboard_search_results_screenshot.png). The user is able to click on another member's [profile](wireframes/dashboard_user_profile_screenshot.png) to view more information.

    - Be able to contact other users and keep a record of our message exchange

        - The user can contact another member by clicking on the member's profile and then click the 'Message' button. This will bring up a modal that allows the user to write a message - see example [here](wireframes/send_message_screenshot.png).

        - If the member is on the user's 'Collaborators' database, the user can access that database and message the member from there by clicking on the 'Message' button attached to that member's thumbnail - see example [here](wireframes/message_via_collaborators_screenshot.png).

        - The 'Messages' button on the user's dashboard allows the user to access new and old [messages](wireframes/messages_screenshot.png). The 'Reply' button on each message allows the user to reply to the message and also keep track of the entire conversation [history](wireframes/reply_screenshot.png).

    - Access a database containing my favourite users

        - The dashboard contains a section entitled 'Collaborators' that allows a user to access his favoutire musicians / collaborators. To add a member to the 'Collaborators' database, the user needs to click on a member's profile and then click the 'Add to Collaborators' button.

        - The 'Collaborators' section has some basic management functionality. The user can message a member or remove them as a collaborator - see example [here](wireframes/collaborators_screenshot.png). It is also possible to remove someone as a collaborator by accessing the member's profile and click the 'Remove from Collaborators' button (only visible if the member is a collaborator).

    - Leave feedback on another member's page

        - This can be done by clicking on a member's profile and then the 'Feedback' button. A modal window pops up, allowing the user to write [feedback](wireframes/feedback_screenshot.png) on someone else. The feedback then appears in the lower section of the profile page.

    - Edit / delete my profile

        - The user dashboard has a section called ['Profile'](wireframes/profile_settings_screenshot.png) that allows users to view, edit and delete their profiles.

        - Clicking the 'Edit' button under 'Profile' will lead the user to an Edit Profile page. This [page](wireframes/edit_profile_screenshot.png) is very similar to the Register page, allowing the user to alter most of the current details.

        -  The 'Delete' button under 'Profile' will delete the user's profile. Once [clicked](wireframes/delete_profile_screenshot.png), a modal window pops up, requesting confirmation from the user.

    - Be able to log out

        - This is done by clicking the 'Logout' button on the top right corner of the screen. Clicking this button will terminate the user's session and lead them back to the main page.

### 4.4 Bugs Encountered and Resolution Steps

1. If the user doesn't upload a picture, nothing shows up in the profile display.

To avoid the above, a generic picture has been uploaded to the MongoDB 'jammers' database, under the 'fs.chunks' and 'fs.files' collection: 'generic_profile_pic.jpg'.

If the user doesn't upload a picture, the code under `register()` and `edit_profile()` in app.py will assign 'generic_profile_pic.jpg' as the user's profile [picture](wireframes/generic_profile_pic_screenshot.png). Example code under `register()`:

```
    if 'profile_pic' in request.files:
        profile_pic = request.files['profile_pic']
        if profile_pic.filename == '':
            profile_pic_name = 'generic_profile_pic.jpg'
        else:
            profile_pic_name = (
                f"{request.form.get('username')}{profile_pic.filename}")

            mongo.save_file(profile_pic_name, profile_pic)
```

2. Multiple entries on 'other_instrument' input on the 'Register' section get entered on database as a single string.

If a user types in "Violin, Cello" for example, if gets entered in the 'users' collection in MongoDB as "violin, cello". To solve this, code was added to the `register()` and `edit_profile()` functions that splits the string and sends multiple entries to MongoDB. Code example for `register()`:

```
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
```

The caveat is that the user needs to use commas to separate multiple values. I thought about adding a condition for spaces, but this will add complications on its own. For example, a user may want to write "Various ethnic instruments" or even simpler "Acoustic Guitar". To ensure the use of commas, the following comment was added to the 'other_instrument' input label: "Other instruments (separate with a comma)".

3. Profile pictures with the same name will cause conflicts on MongoDB.

There may be occasions where multiple users upload a profile picture with the same name (for example, two users may upload a picture called 'profile.jpg'). This will cause a conflict on the database and some users will not see their profile picture displayed correctly.

To avoid this, each file needs to have a unique name. In this case, we're adding the username to the file's original name:

```
    profile_pic_name = (
        f"{request.form.get('username')}{profile_pic.filename}")
```