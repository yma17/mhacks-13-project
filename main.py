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

def in_room(room):
    # check if session exists, if not redirect user to login page
    try:
        print(session['usr'])
        # Todo: replace 1 with user id
        return session['usrId'] in room["users"]
    except KeyError:
        return redirect(url_for('login'))

def both_in_room(room, me, user):
    # Todo: replace 1 with user id
    return me in room["users"] and user in room["users"]

@app.route('/chat', methods=['GET', 'POST'])
def chat_list():
    # check if session exists, if not redirect user to login page
    try:
        print(session['usr'])
        all_rooms = db.child("rooms").get().val()
        # first room is None for some reason
        # all_rooms.pop(0)
        rooms = list(filter(in_room, all_rooms))
        # Todo: replace current_user id // NOT DONE YET
        return render_template('chat_list.html', rooms=rooms, current_user=session['usrId'])
    except KeyError:
        return redirect(url_for('login'))


# triggered from chat page / exchange button
@app.route('/chat/<room_id>', methods=['GET', 'POST'])
def chat(room_id):
    # check if session exists, if not redirect user to login page
    try:
        print(session['usr'])
        # Todo: avoid querying twice
        messages = db.child(f"rooms/{room_id}/messages").get().val()
        users = db.child(f"rooms/{room_id}/users").get().val()
        my_name = db.child(f"users/{session['usrId']}/Name").get().val()
        
        chat_name = db.child(f"rooms/{room_id}/usernames").get().val()
        chat_name.remove(my_name)
        chat_name = chat_name[0]

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
        return render_template('chat.html', messages=messages, room_id=room_id, users=users, current_user=session['usrId'], chat_name=chat_name)
    
    except KeyError:
        return redirect(url_for('login'))

# @app.route("/index", methods=["GET", "POST"])
# def explore():
#     if request.method == "POST": 
#         all_rooms = db.child("rooms").get().val()
#         room_id = 0
#         if all_rooms is not None:
#             # first room is None for some reason
#             all_rooms.pop(0)
#             rooms = list(filter(lambda room: both_in_room(room, "0hxF9MYWbjfbp9cVN0dOi8mmVkj1", "2b0er64qPkRaCItSRd0xCY7INil1"), all_rooms))

#             if len(rooms) < 1:
#                 # create room
#                 # replace users with current user id and other user id
#                 db.child("rooms").child(len(all_rooms)).set({"users": ["0hxF9MYWbjfbp9cVN0dOi8mmVkj1", "2b0er64qPkRaCItSRd0xCY7INil1"], "messages": [{}]})
#                 room_id = len(all_rooms)
#             else:
#                 # store room
#                 room_id = rooms[0]
#         else:
#             db.child("rooms").child(0).set({"users": ["0hxF9MYWbjfbp9cVN0dOi8mmVkj1", "2b0er64qPkRaCItSRd0xCY7INil1"], "messages": [{}]})
#             room_id = 0
#         return redirect(url_for('chat', room_id=room_id))
    
#     return render_template('index.html')
  
@app.route("/index", methods=["GET", "POST"])
def index():
    # check if session exists, if not redirect user to login page
    try:
        print(session['usr'])
        data = {'users': db.child("users").get().val(),
                'uid': session['usrId']}

        if request.method == "POST": 
            other_user = request.form['userId']
            other_user_name = db.child(f"users/{other_user}/Name").get().val()
            my_name = db.child(f"users/{session['usrId']}/Name").get().val()

            all_rooms = db.child("rooms").get().val()
            room_id = 0
            if all_rooms is not None:
                # first room is None for some reason
                # all_rooms.pop(0)
                rooms = list(filter(lambda room: both_in_room(room, session['usrId'], other_user), all_rooms))

                if len(rooms) < 1:
                    # create room
                    # replace users with current user id and other user id
                    db.child("rooms").child(len(all_rooms)).set({"users": [session['usrId'], other_user], "usernames": [my_name, other_user_name], "messages": [{}]})
                    room_id = len(all_rooms)
                else:
                    # store room
                    # room_id = rooms[0]
                    room_id = all_rooms.index(rooms[0])
            else:
                db.child("rooms").child(0).set({"users": [session['usrId'], other_user], "usernames": [my_name, other_user_name], "messages": [{}]})
                room_id = 0
            return redirect(url_for('chat', room_id=room_id))


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