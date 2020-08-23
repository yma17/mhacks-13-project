import csv

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


readRecFromCsv()