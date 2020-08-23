import csv
import pyrebase

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

def readRecFromCsv():
    # read all user ids first
    with open('uid.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        id_list = []
        for i in next(csv_reader):
            id_list.append(i)

    # get specific index of current user, to get row of predictions
    idx = id_list.index("zxcZAXnIA0dDNYQKvSx81AcTXIg2")

    with open('lt_matrix.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        pred = {}
        selectedRow = [row for i, row in enumerate(csv_reader) if i == idx]
        for i, val in enumerate(selectedRow[0]):
            # exclude current user
            if (i == idx):
                continue
            pred[id_list[i]] = val
        
    return pred

# only ran once to setup photos
def uploadPhotos():
    filePath = 'profilepic/' + session['usrId']
    storage.child(filePath).put(file, session['usr'])