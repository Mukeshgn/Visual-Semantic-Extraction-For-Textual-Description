from flask import Flask, render_template, redirect, request, session, url_for
import pyrebase
import subprocess
from script import generate_image_caption
import os

app = Flask(__name__)

# Firebase configuration
firebaseConfig = {
    "apiKey": "AIzaSyAxb0Y4-V3ttf2M4i2SNL-uwh0dFW-oKqg",
    "authDomain": "captioning-auth.firebaseapp.com",
    "projectId": "captioning-auth",
    "storageBucket": "captioning-auth.appspot.com",
    "messagingSenderId": "820676668939",
    "appId": "1:820676668939:web:04de0a7d50ef545971610e",
    "measurementId": "G-EEB08HVN22",
    "databaseURL" : "https://captioning-auth.firebaseio.com"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# Route for handling signup form submission
@app.route('/signup', methods=['POST'])
def signup_post():
    email = request.form['email']
    password = request.form['password']

    try:
        # Create a new user with email and password
        user = auth.create_user_with_email_and_password(email, password)
        session['user'] = user['email']  # Store user email in session
        return redirect('/profile')
    except Exception as e:
        error_message = str(e)
        if 'EMAIL_EXISTS' in error_message:
            session['error_message'] = 'Email already exists'
        else:
            session['error_message'] = 'An error occurred'  # Generic error message
        return redirect('/signup')

# Route for login page
@app.route('/')
def login():
    error_message = session.pop('error_message', None)  # Get error message from session
    return render_template('login.html', error_message=error_message)

# Route for signup page
@app.route('/signup')
def signup():
    error_message = session.pop('error_message', None)  # Get error message from session
    return render_template('signup.html', error_message=error_message)


# Route for handling login form submission
@app.route('/login', methods=['POST'])
def login_post():
    email = request.form['email']
    password = request.form['password']

    try:
        # Sign in the user with email and password
        user = auth.sign_in_with_email_and_password(email, password)
        session['user'] = user['email']  # Store user email in session
        return redirect('/profile')
    except Exception as e:
        session['error_message'] = 'Wrong credentials'  # Store error message in session
        return redirect('/')


# Route for profile page
@app.route('/profile')
def profile():
    # Check if user is logged in
    if 'user' in session:
        user_email = session['user']
        return render_template('profile.html', email=user_email)
    else:
        return redirect('/')

# Route for logout
@app.route('/logout')
def logout():
    # Clear session data to log out the user
    session.clear()
    return redirect('/')


# Route for uploading image
@app.route('/upload_image', methods=['POST'])
def upload_image():
    user_email = session['user']
    if 'image' in request.files:
        image = request.files['image']
        # Process the uploaded image (e.g., save it to disk, perform image captioning)
        # Example: Save the uploaded image to a directory
        image_path = 'uploads/' + image.filename
        print(image_path)
        image.save(image_path)

        # Run a Python script with the uploaded image as input
        image_caption = generate_image_caption(image_path)

        # Redirect to profile page and pass the output to be displayed
        return render_template('profile.html', image_caption=image_caption, image_path=os.path.abspath(image_path), email=user_email)
    return redirect('/profile')



if __name__ == '__main__':
    app.secret_key = 'supersecretkey'
    app.run(debug=True)