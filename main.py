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

<<<<<<< HEAD
@app.route("/chat")
def chat():
    return render_template("chat.html")
=======
@app.route('/profile/')
def about():
    print(db.get())
    return render_template('profile.html', data=db.get().val())
>>>>>>> master

if __name__ == "__main__":
    app.run()