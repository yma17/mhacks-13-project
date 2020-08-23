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
def index():
    # check if session exists, if not redirect user to login page
    try:
        print(session['usr'])
        return render_template("index.html", uid= session['usrId'])
    except KeyError:
        return render_template('login.html')

@app.route("/index")
def index2():
    # check if session exists, if not redirect user to login page
    try:
        print(session['usr'])
        return render_template("index.html", uid= session['usrId'])
    except KeyError:
        return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ""
    # if session exists, redirect to index page
    try:
        print(session['usr'])
        return render_template("index.html", uid= session['usrId'])
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
                return render_template("index.html", uid=session['usrId'])
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
            return render_template('profile.html', uid=user)
        # if registration unsuccessful, return to registration page
        except:
            message = "Unable to register. Please try again"
            return render_template('register.html')
    return render_template('register.html', message=message)

@app.route('/profile')
def profile():
    # check if session exists, if not redirect user to login page
    try:
        print(session['usr'])
        # list of skills that can be added
        skills = ['Cooking', 'Coding', 'Baking', 'Writing', 'Sewing', 
        'Knitting', 'Photoshop', 'Photography', 'Singing', 'Gardening', 
        'Meditation', 'Video Editing', 'Drawing', 'Painting', 'Reading', 
        'English', 'Spanish', 'Chinese', 'French','German', 'Japanese', 
        'Korean', 'Hindu', 'Arabic', 'Malay', 'Italian', 'Portuguese']


        # query to get correct user based on userID from session
        user = db.child("users").child(session['usrId']).get()
        if (user == None): 
            message = "Sorry, we are having issues finding your profile."
            return render_template('login.html', message=message)

        data = {'user': user.val(),
                'email': auth.get_account_info(session['usr'])['users'][0]['email'],
                'allSkills' : skills,
                'picsrc': storage.child('cat.jpg').get_url('8w3Sb016P9Yu3S0cTarcId9jVkd2')}
        return render_template('profile.html', **data)
    except KeyError:
        return render_template('login.html')

#Update profile (interest and skills)
@app.route('/updateInterest', methods=['GET', 'POST'])
def updateInterest():
    if request.method != 'POST':
        interest = request.form['interest']
        interestLevel = request.form['interestLevel']
        data = {interest: interestLevel}
        db.child("users").child(session['usrId']).child("Interests").push(data)
    return redirect(url_for('profile'))

@app.route('/updateSkill', methods=['GET', 'POST'])
def updateSkill():
    if request.method != 'POST':
        skill = request.form['skill']
        skillLevel = request.form['skillLevel']
        data = {skill: skillLevel}
        db.child("users").child(session['usrId']).child("Skills").push(data)
    return redirect(url_for('profile'))

if __name__ == "__main__":
    app.run(debug=True)