import os
import csv
import time
import pyrebase
from flask import Flask, render_template, session, request, redirect, url_for
from urllib.parse import urlparse
from random import randint
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

# Initialize Flask App
app = Flask(__name__)
app.secret_key = os.urandom(24)

def readRecFromCsv():
    # download uid.csv and lt_matrix.csv from firebase storage
    #storage.child("uid.csv").download("uid.csv")
    #storage.child("lt_matrix.csv").download("lt_matrix.csv")

    # read all user ids first
    with open('uid.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        id_list = []
        count = 0
        for i in next(csv_reader):
            id_list.append(i)
            # run once to fill with profile pictures for each user id
            # if count >= 450 and count < 550:
            #     print(count)
            #     curr = (count % 5) + 1
            #     filePath = 'profilepic/' + i
            #     srcPath = "static/assets/img/avatars/avatar" + str(curr) + ".jpeg"
            #     storage.child(filePath).put(srcPath, session['usr'])
            # count = count + 1


    if session['usrId'] in id_list:
        # get specific index of current user, to get row of predictions
        idx = id_list.index(session['usrId'])
    else:
        try:
            # get row of nearest neighbor from shared interests
            highest_sim = 0

            users = db.child("users").get()
            for uid, user_info in users.items():
                if "Interests" in user_info:
                    this_sim = 0
                    for interest, level in user_info["Interests"].items():
                        if interest in user_info[session['usrId']]["Interests"]:
                            level_diff = abs(level - user_info[session['usrId']]["Interests"][interest])
                            if level_diff == 0:
                                this_sim += 5
                            elif level_diff == 1:
                                this_sim += 3
                            elif level_diff == 2:
                                this_sim += 1
                    if this_sim > highest_sim:
                        highest_sim = this_sim
                        idx = uid
        except:
            idx = 0

    with open('lt_matrix.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        pred = {}
        selectedRow = [row for i, row in enumerate(csv_reader) if i == idx]
        for i, val in enumerate(selectedRow[0]):
            # exclude current user
            if (i == idx):
                continue
            pred[id_list[i]] = float(val)

    return pred

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
        print(room_id)
        
        chat_name = db.child(f"rooms/{room_id}/usernames").get().val()
        print(db.child(f"rooms/{room_id}/usernames").get().val())
        chat_name.remove(my_name)
        chat_name = chat_name[0]
        print("chat name", chat_name)

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
        # user has been logged out
        if(session['usr'] == None):
            return redirect(url_for('login'))

        # receive the list of uids then sort (excludes current user)
        uidDict = readRecFromCsv()
        #sorted_teachers = {k: v for k, v in sorted(uidDict.items(), key=lambda x: x[1])}
        sorted_teachers = sorted(uidDict.items(), key=operator.itemgetter(1),reverse=True)
        if len(sorted_teachers) > 50:
            sorted_teachers = sorted_teachers[:50]
        sorted_teachers = dict(sorted_teachers)

        # attempt to get photo for current user, if not found revert to default
        filePath = "profilepic/" + session['usrId']
        url = storage.child(filePath).get_url(session['usrId'])
        response = urllib.request.urlopen(url)
        if response.code not in range(200, 209):
            url = '/static/assets/img/default.jpg'

        colors = ['primary', 'success', 'warning', 'danger', 'warning']

        data = {'users': db.child("users").get().val(),
                'uid': session['usrId'],
                'url': url,
                'teachers': sorted_teachers, 
                'colors': colors}

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
        # user has been logged out
        if(session['usr'] == None):
            return render_template("login.html", message=message)
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
        # user has been logged out
        if(session['usr'] == None):
            return redirect(url_for('login'))

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

        # get profile picture of self
        filePath = 'profilepic/' + session['usrId']
        profilePicture = storage.child(filePath).get_url(session['usrId'])
        try:
            response = urllib.request.urlopen(url)
        except:
            url = storage.child("profilepic/default.jpg").get_url(session['usr'])

        data = {'user': user.val(),
                'email': auth.get_account_info(session['usr'])['users'][0]['email'],
                'allSkills' : skills,
                'picsrc': storage.child(filePath).get_url(session['usr']),
                'url': url}
        return render_template('profile.html', **data)
    except KeyError:
        return redirect(url_for('login'))

# If want to know about other people's profiles
@app.route('/otherProfile/')
def otherProfile():
    try:
        print(session['usr'])
        # user has been logged out
        if(session['usr'] == None):
            return redirect(url_for('login'))

        userId = request.args.get('userId')
        status = request.args.get('status')
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
        
        filePath = "profilepic/" + userId
        url = storage.child(filePath).get_url(userId)
        try:
            response = urllib.request.urlopen(url)
        except:
            url = storage.child("profilepic/default.jpg").get_url(session['usr'])

        filePath = 'profilepic/' + session['usrId']
        profilePicture = storage.child(filePath).get_url(session['usrId'])
        try:
            response = urllib.request.urlopen(url)
        except:
            url = storage.child("profilepic/default.jpg").get_url(session['usr'])
        
        data = {'users': db.child("users").get().val(),
                'uid': session['usrId'],
                'otheruid': userId,
                'user': user,
                'skills': sorted_skills,
                'interests': sorted_interests, 
                'url': url,
                'profilePicture': profilePicture,
                'status': status}

        return render_template('otherProfile.html', **data)
    
    except KeyError:
        return redirect(url_for('login'))


# Upload/change profile picture
@app.route('/updatePhoto', methods=['GET', 'POST'])
def updatePhoto():
    if request.method == 'POST':
        file = request.files['file']
        filePath = "profilepic/" + session['usrId']
        storage.child(filePath).put(file, session['usr'])
    return redirect(url_for('profile'))

# Sign out
@app.route('/signOut')
def signOut():
    session['usrId'] = None
    session['usr'] = None
    return redirect(url_for('home'))

# Pay currency from current user to other user
@app.route('/payCurrency', methods=['GET', 'POST'])
def payCurrency():
    fromId = session['usrId']
    toId = request.form['otherId']

    try: 
        # get database entries of both users
        fromAmount = db.child("users").child(fromId).child("currency").get().val()
        toAmount = db.child("users").child(toId).child("currency").get().val()

        fromAmount = int(fromAmount) - 1
        toAmount = int(toAmount) - 1

        if fromAmount <= 0:
            return redirect('/otherProfile/?userId=' + str(toId) + '&status=insufficient')

        # update database entries of both users: from - 1, to + 1
        db.child("users").child(fromId).child("currency").set(fromAmount)
        db.child("users").child(fromId).child("currency").set(toAmount)

        return redirect('/otherProfile/?userId=' + str(toId) + '&status=paid')

    except:
        return redirect('/otherProfile/?userId=' + str(toId) + '&status=failed')

if __name__ == "__main__":
    app.run(debug=True)

