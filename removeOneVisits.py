import csv

icdIN = open('ICD9.csv','rb')
icdOUT = open('ICD-9.csv','wb')
input_reader = csv.reader(icdIN)
output_writer = csv.writer(icdOUT)
mDict = {}
keyCounts = {}

while True:
    try:
        row = input_reader.next()
        key = str(row[0]) + "-" + str(row[1])
        if key in mDict:
            mDict[key].append(row)
        else:
            mDict[key] = [row]
            if row[0] not in keyCounts:
                keyCounts[row[0]] = 0
            keyCounts[row[0]] += 1
    except:
        break


for key in mDict:
    print key
    new_key = key.split("-")[0]
    print new_key
    if keyCounts[new_key] > 1:
        for row in mDict[key]:
            output_writer.writerow(row)
        print keyCounts[new_key], len(mDict[key])