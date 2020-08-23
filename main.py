import pyrebase
from flask import Flask, render_template

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
    return render_template('otherProfile.html', users = db.child("users").get().val())

if __name__ == "__main__":
    app.run()