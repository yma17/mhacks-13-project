import pyrebase
import random
import pickle
import csv

config = {
	"apiKey": "AIzaSyAQk0A5csVTIUIEfvdXXiXaelEG3OWes9U",
	"authDomain": "mhacks-13-project.firebaseapp.com",
	"databaseURL": "https://mhacks-13-project.firebaseio.com",
	"storageBucket": "mhacks-13-project.appspot.com"
}

firebase = pyrebase.initialize_app(config)

db = firebase.database()

# skills=['Cooking', 'Coding', 'Baking', 'Writing', 'Sewing', 'Knitting', 'Photoshop', 'Photography',
#         'Singing', 'Gardening', 'Meditation', 'Video Editing', 'Drawing', 'Painting', 'Reading’, ''English',
#         'Spanish', 'Chinese', 'French', 'German', 'Japanese', 'Korean', 'Hindu', 'Arabic', 'Malay', 'Italian', 'Portuguese']

names = []
with open('babynames-clean.csv', newline='') as csvfile:
	name_reader = csv.reader(csvfile, delimiter=',',quotechar='|')
	for row in name_reader:
		names.append(row[0])

skill_prob_dict={
	'Cooking':0.06,
	'Coding':0.2,
	'Baking':0.1,
	'Writing':0.07,
	'Sewing':0.05,
	'Knitting':0.04,
	'Photoshop':0.08,
	'Photography':0.1,
    'Singing':0.04,
    'Gardening':0.05,
    'Meditation':0.16,
    'Video Editing':0.05,
    'Drawing':0.09,
    'Painting':0.05,
    'Reading':0.09,
    'English':0.13,
    'Spanish':0.19,
    'Chinese':0.17,
    'French':0.04,
    'German':0.03,
    'Japanese':0.03,
    'Korean':0.04,
    'Hindu':0.15,
    'Arabic':0.04,
    'Malay':0.03,
    'Italian':0.03,
    'Portuguese':0.03
}

interest_dist = [1, 1, 1, 1, 1, 2, 2, 2, 3, 3]

with open('uids.pickle', 'rb') as uid_file:
	uids = pickle.load(uid_file)

for uid in uids:
	name = random.choice(names)
	currency = random.randint(0, 10)
	skills={}
	interests={}
	for k, v in skill_prob_dict.items():
		r = random.random()
		if r <= v:
			i = random.choice(interest_dist)
			interests[k] = i
			skills[k] = random.randint(0, i - 1)
		elif r >= 0.99:
			skills[k] = 3

	db.child("users").child(str(uid)).set({'Name':name, 'currency':currency, 'Interests':interests, 'Skills':skills})
