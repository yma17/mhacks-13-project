import pyrebase
from flask import Flask, render_template, request
import urllib.parse as urlparse
from urllib.parse import parse_qs

config = {
  "apiKey": "AIzaSyAQk0A5csVTIUIEfvdXXiXaelEG3OWes9U",
  "authDomain": "mhacks-13-project.firebaseapp.com",
  "databaseURL": "https://mhacks-13-project.firebaseio.com",
  "storageBucket": "mhacks-13-project.appspot.com"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

# Initialize Flask App
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/register")
def register():
    return render_template('register.html')

@app.route("/index")
def explore():
    return render_template('index.html',  users = db.child("users").get().val())
  
@app.route('/profile/')
def about():
    print(db.get())
    return render_template('profile.html', data=db.get().val())

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

if __name__ == "__main__":
    app.run()