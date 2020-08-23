import os
import pyrebase

from flask import Flask, render_template, session, request, redirect, url_for
from urllib.parse import urlparse
import urllib.request
import operator
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

# list of skills that can be added
SKILLS = ['Cooking', 'Coding', 'Baking', 'Writing', 'Sewing', 
'Knitting', 'Photoshop', 'Photography', 'Singing', 'Gardening', 
'Meditation', 'Video Editing', 'Drawing', 'Painting', 'Reading', 
'English', 'Spanish', 'Chinese', 'French','German', 'Japanese', 
'Korean', 'Hindu', 'Arabic', 'Malay', 'Italian', 'Portuguese']

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
        # receive the list of uids then sort
        uidDict = {'0EeM4SlVTeNEkzx2r6dziAirPBO2': '0', '0GZkZYJfJZNI0r7gieDq4v9Zmeo1': '1', '0g6DIZAxYbejOSQsn0U0FYcpl3I3': '0.5', '0hxF9MYWbjfbp9cVN0dOi8mmVkj1': '1'}
        #sorted_teachers = {k: v for k, v in sorted(uidDict.items(), key=lambda x: x[1])}
        sorted_teachers = dict(sorted(uidDict.items(), key=operator.itemgetter(1),reverse=True))
        filePath = "profilepic/" + session['usrId']
        url = storage.child(filePath).get_url(session['usrId'])

        response = urllib.request.urlopen(url)
        if response.code not in range(200, 209):
            url = urlparse(
                'https://firebasestorage.googleapis.com/v0/b/mhacks-13-project.appspot.com/o/profilepic%2FeyJhbGciOiJSUzI1NiIsImtpZCI6IjEyODA5ZGQyMzlkMjRiZDM3OWMwYWQxOTFmOGIwZWRjZGI5ZDM5MTQiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vbWhhY2tzLTEzLXByb2plY3QiLCJhdWQiOiJtaGFja3MtMTMtcHJvamVjdCIsImF1dGhfdGltZSI6MTU5ODE1NjUxMCwidXNlcl9pZCI6IklGbHQwYkVJR01YNWwxblhWSzV4b1lyNmViZjEiLCJzdWIiOiJJRmx0MGJFSUdNWDVsMW5YVks1eG9ZcjZlYmYxIiwiaWF0IjoxNTk4MTU2NTEwLCJleHAiOjE1OTgxNjAxMTAsImVtYWlsIjoic2lt'
            )
        return render_template('index.html', **data, teachers = sorted_teachers, url = url)
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
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        skill = request.form['skill']
        interest = request.form['interest']
        try:
            # create entry in auth table
            user = auth.create_user_with_email_and_password(email, password)
            user = auth.refresh(user['refreshToken'])
            session['usr'] = user['idToken']
            session['usrId'] = auth.get_account_info(session['usr'])['users'][0]['localId']

            # create entry in realtime database
            # Set interests, Name, Skills, currency
            newData = { 'Interests': {interest: 0}, 
                        'Name': username,
                        'Skills': {skill: 0},
                        'currency': 5}
            db.child("users").child(session['usrId']).set(newData)
            
            # put default profile pic
            filePath = "profilepic/" + session['usrId']
            storage.child(filePath).put("default.jpg", user['idToken'])
            return redirect(url_for('profile'))
        # if registration unsuccessful, return to registration page
        except:
            message = "Unable to register. Please try again"
    data= {'message': message,
            'allSkills': SKILLS}
    return render_template('register.html', **data)

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

        # query to get correct user based on userID from session
        user = db.child("users").child(session['usrId']).get()
        filePath = "profilepic/" + session['usrId']

        data = {'user': user.val(),
                'email': auth.get_account_info(session['usr'])['users'][0]['email'],
                'allSkills' : SKILLS,
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
    skills = dict()
    interests = dict()
    if "Skills" in users[userId]:
        skills = users[userId]["Skills"]
    if "Interests" in users[userId]:
        interests = users[userId]["Interests"]
    sorted_interests = {k: v for k, v in sorted(interests.items(), key=lambda x: x[1])}
    sorted_skills = {k: v for k, v in sorted(skills.items(), key=lambda x: x[1])}
    
    filePath = "profilepic/" + session['usrId']
    url = storage.child(filePath).get_url(session['usrId'])
    
    
    response = urllib.request.urlopen(url)
    if response.code not in range(200, 209):
        url = urlparse(
            'https://firebasestorage.googleapis.com/v0/b/mhacks-13-project.appspot.com/o/profilepic%2FeyJhbGciOiJSUzI1NiIsImtpZCI6IjEyODA5ZGQyMzlkMjRiZDM3OWMwYWQxOTFmOGIwZWRjZGI5ZDM5MTQiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vbWhhY2tzLTEzLXByb2plY3QiLCJhdWQiOiJtaGFja3MtMTMtcHJvamVjdCIsImF1dGhfdGltZSI6MTU5ODE1NjUxMCwidXNlcl9pZCI6IklGbHQwYkVJR01YNWwxblhWSzV4b1lyNmViZjEiLCJzdWIiOiJJRmx0MGJFSUdNWDVsMW5YVks1eG9ZcjZlYmYxIiwiaWF0IjoxNTk4MTU2NTEwLCJleHAiOjE1OTgxNjAxMTAsImVtYWlsIjoic2lt'
        )
    return render_template('otherProfile.html', user = user, skills = sorted_skills, interests = sorted_interests, url = url)

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