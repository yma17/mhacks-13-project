import pyrebase
from flask import Flask, render_template, request

config = {
  "apiKey": "AIzaSyAQk0A5csVTIUIEfvdXXiXaelEG3OWes9U",
  "authDomain": "mhacks-13-project.firebaseapp.com",
  "databaseURL": "https://mhacks-13-project.firebaseio.com",
  "storageBucket": "mhacks-13-project.appspot.com"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

# db.child("names").push({"name": "chloe"})

# Initialize Flask App
app = Flask(__name__)
# socketio = SocketIO(app)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/test")
def test():
    return render_template("test.html")

@app.route('/chat/', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        # print(db.child('messages').get().val())
        # userId = request.form['userId']
        message = request.form['message']
        db.child("messages").push({"message": message})
        # db.child("rooms").push({'room1': {"user": userId, "message": message}})
    return render_template('chat.html')

@app.route('/profile/')
def about():
    print(db.get())
    return render_template('profile.html', data=db.get().val())

# @socketio.on('send_message')
# def handle_send_message_event(data):
#     # notify all users
#     socketio.emit("receive_message", data, room=data['room'])

if __name__ == "__main__":
    app.run(debug=True)
    # socketio.run(app)