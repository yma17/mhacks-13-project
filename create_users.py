import pyrebase
import pickle

config = {
	"apiKey": "AIzaSyAQk0A5csVTIUIEfvdXXiXaelEG3OWes9U",
	"authDomain": "mhacks-13-project.firebaseapp.com",
	"databaseURL": "https://mhacks-13-project.firebaseio.com",
	"storageBucket": "mhacks-13-project.appspot.com"
}

firebase = pyrebase.initialize_app(config)

auth = firebase.auth()

uids = []

for i in range(471, 501):
	x = auth.create_user_with_email_and_password("fakeemail" + str(i) + "@gmail.com", "password" + str(i))
	uids.append(x['localId'])
	print(x['localId'])

# with open('uids.pickle', 'wb') as handle:
# 	pickle.dump(uids, handle)