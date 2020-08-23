import pyrebase
from flask import Flask, render_template, request, redirect, url_for

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

def in_room(room):
    # Todo: replace 1 with user id
    return "0hxF9MYWbjfbp9cVN0dOi8mmVkj1" in room["users"]

def both_in_room(room, me, user):
    # Todo: replace 1 with user id
    return me in room["users"] and user in room["users"]

@app.route('/chat', methods=['GET', 'POST'])
def chat_list():
    all_rooms = db.child("rooms").get().val()
    # first room is None for some reason
    all_rooms.pop(0)
    rooms = list(filter(in_room, all_rooms))
    # Todo: replace current_user id // NOT DONE YET
    return render_template('chat_list.html', rooms=rooms, current_user="0hxF9MYWbjfbp9cVN0dOi8mmVkj1")

# triggered from chat page / exchange button
@app.route('/chat/<room_id>', methods=['GET', 'POST'])
def chat(room_id):
    # Todo: avoid querying twice
    messages = db.child(f"rooms/{room_id}/messages").get().val()
    users = db.child(f"rooms/{room_id}/users").get().val()
    usernames = db.child(f"rooms/{room_id}/usernames").get().val()

    if request.method == 'POST':
        user_id = request.form['user_id']
        username = db.child(f"users/{user_id}/Name").get().val()
        message = request.form['message']

        if message: 
            if messages != None:
                db.child(f"rooms/{room_id}/messages").child(len(messages)).set({"message": message, "user_id": user_id, "username": username})
            else:
                db.child(f"rooms/{room_id}/messages").child(0).set({"message": message, "user_id": user_id, "username": username})

    # make sure to retrieve new messages
    messages = db.child(f"rooms/{room_id}/messages").get().val()
    return render_template('chat.html', messages=messages, room_id=room_id, users=users)

@app.route("/index", methods=["GET", "POST"])
def explore():
    if request.method == "POST": 
        all_rooms = db.child("rooms").get().val()
        room_id = 0
        if all_rooms is not None:
            # first room is None for some reason
            all_rooms.pop(0)
            rooms = list(filter(lambda room: both_in_room(room, "0hxF9MYWbjfbp9cVN0dOi8mmVkj1", "2b0er64qPkRaCItSRd0xCY7INil1"), all_rooms))

            if len(rooms) < 1:
                # create room
                # replace users with current user id and other user id
                db.child("rooms").child(len(all_rooms)).set({"users": ["0hxF9MYWbjfbp9cVN0dOi8mmVkj1", "2b0er64qPkRaCItSRd0xCY7INil1"], "messages": [{}]})
                room_id = len(all_rooms)
            else:
                # store room
                room_id = rooms[0]
        else:
            db.child("rooms").child(0).set({"users": ["0hxF9MYWbjfbp9cVN0dOi8mmVkj1", "2b0er64qPkRaCItSRd0xCY7INil1"], "messages": [{}]})
            room_id = 0
        return redirect(url_for('chat', room_id=room_id))
    
    return render_template('index.html')

@app.route('/table')
def table():
    return render_template('table.html') 
  
@app.route('/profile/')
def about():
    print(db.get())
    return render_template('profile.html', data=db.get().val())

if __name__ == "__main__":
    app.run(debug=True)