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
    return render_template('index.html')

@app.route("/index")
def index2():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ""
    try:
        print(session['usr'])
        return redirect(url_for('index'))
    except KeyError:
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                user = auth.refresh(user['refreshToken'])
                user_id = user['idToken']
                session['usr'] = user_id
                return redirect(url_for('index'))
            except:
                message = "Incorrect Password!"
        return render_template("login.html", message=message)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            auth.create_user_with_email_and_password(email, password)
            return render_template('index.html')
        except:
            return render_template('register.html')
    return render_template('register.html')

@app.route('/profile/')
def profile():
    data = {'db': db.get(),
            'picsrc': storage.child('cat.jpg').get_url('8w3Sb016P9Yu3S0cTarcId9jVkd2')}
    return render_template('profile.html', **data)

if __name__ == "__main__":
    app.run(debug=True)