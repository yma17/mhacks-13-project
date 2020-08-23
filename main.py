import os
import pyrebase

from flask import Flask, render_template, session, request, redirect, url_for

config = {
  "apiKey": "AIzaSyAQk0A5csVTIUIEfvdXXiXaelEG3OWes9U",
  "authDomain": "mhacks-13-project.firebaseapp.com",
  "databaseURL": "https://mhacks-13-project.firebaseio.com",
  "storageBucket": "mhacks-13-project.appspot.com",
  "serviceAccount": "key.json"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()

# Initialize Flask App
app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/index")
def index():
    # check if session exists, if not redirect user to login page
    try:
        print(session['usr'])
        data = {'users': db.child("users").get().val(),
                'uid': session['usrId']}
        return render_template('index.html', **data)
    except KeyError:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ""
    # if session exists, redirect to index page
    try:
        print(session['usr'])
        return redirect(url_for('index'))
    # session does not exist
    except KeyError:
        # login form submission
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                user = auth.refresh(user['refreshToken'])
                session['usr'] = user['idToken']
                session['usrId'] = auth.get_account_info(session['usr'])['users'][0]['localId']
                # redirect to index page
                return redirect(url_for('index'))
            # if login unsuccessful, return to login page
            except:
                message = "Incorrect Password!"
        return render_template("login.html", message=message)

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ""
    # register form submission
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.create_user_with_email_and_password(email, password)
            user = auth.refresh(user['refreshToken'])
            session['usr'] = user['idToken']
            session['usrId'] = auth.get_account_info(session['usr'])['users'][0]['localId']
            # put default profile pic
            filePath = "profilepic/" + session['usrId']
            storage.child(filePath).put("/static/assets/img/default.jpg", session['usr'])
            return redirect(url_for('profile'))
        # if registration unsuccessful, return to registration page
        except:
            message = "Unable to register. Please try again"
            return render_template('register.html')
    return render_template('register.html', message=message)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    # check if session exists, if not redirect user to login page
    try:
        print(session['usr'])

        if request.method == 'POST':
            data = request.get_json()
            skills = data['Skills']
            interests = data['Interests']
            # update profile
            user = db.child("users").child(session['usrId']).child("Skills").set(skills)
            user = db.child("users").child(session['usrId']).child("Interests").set(interests)
        

        # list of skills that can be added
        skills = ['Cooking', 'Coding', 'Baking', 'Writing', 'Sewing', 
        'Knitting', 'Photoshop', 'Photography', 'Singing', 'Gardening', 
        'Meditation', 'Video Editing', 'Drawing', 'Painting', 'Reading', 
        'English', 'Spanish', 'Chinese', 'French','German', 'Japanese', 
        'Korean', 'Hindu', 'Arabic', 'Malay', 'Italian', 'Portuguese']


        # query to get correct user based on userID from session
        user = db.child("users").child(session['usrId']).get()
        filePath = "profilepic/" + session['usrId']

        data = {'user': user.val(),
                'email': auth.get_account_info(session['usr'])['users'][0]['email'],
                'allSkills' : skills,
                'picsrc': storage.child(filePath).get_url(session['usr'])}
        return render_template('profile.html', **data)
    except KeyError:
        return redirect(url_for('login'))

# If want to know about other people's profiles
@app.route('/otherProfile/')
def otherProfile():
    userId = request.args.get('userId')
    users = db.child("users").get().val()
    user = users[userId]
    skills = users[userId]["Skills"]
    interests = users[userId]["Interests"]
    sorted_interests = {k: v for k, v in sorted(interests.items(), key=lambda x: x[1])}
    sorted_skills = {k: v for k, v in sorted(skills.items(), key=lambda x: x[1])}
    return render_template('otherProfile.html', user = user, skills = sorted_skills, interests = sorted_interests)

# Upload/change profile picture
@app.route('/updatePhoto', methods=['GET', 'POST'])
def updatePhoto():
    if request.method == 'POST':
        file = request.files['file']
        filePath = "profilepic/" + session['usrId']
        storage.child(filePath).put(file, session['usr'])
    return redirect(url_for('profile'))

if __name__ == "__main__":
    app.run(debug=True)