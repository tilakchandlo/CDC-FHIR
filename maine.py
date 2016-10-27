import csv,string,time,sys,sqlite3,os
import numpy as np
from operator import itemgetter

startTime = time.time()

numOverOne = 0
maxValue = 0
maxStays = -1
s = ""
subj_ICDs = {}
maxConditions = []

INFO_DEBUG = False
PERCENT_DEBUG = True
MAX_DEGREE = 3

with open('ICD-9.csv','rb') as ICD9file:
    ICD9reader = csv.reader(ICD9file)
    headerRow = True
    while True:
        try:
            row = ICD9reader.next()
            subject_id = row[0]
            hadm_id = row[1]
            sequence = row[2]
            code = row[3]
            try: # If subject has been seen before
                subj_ICDs[subject_id] # If subject has been seen before
                try:
                    subj_ICDs[subject_id][hadm_id] # If we're on the same hospital stay as the previous line
                    subj_ICDs[subject_id][hadm_id].append((sequence,code)) # Add stay info onto currently appending hospital stay
                except:
                    subj_ICDs[subject_id][hadm_id] = ['Jan 18 2016', (sequence,code)] # Else first hospital admit Id for this already seen subject
            except:
                subj_ICDs[subject_id] = {} # New subject, initialize dict at that key
                subj_ICDs[subject_id][hadm_id] = ['Jan 18 2016', (sequence,code)] # Then initialize hospital stay data for the new subject
        except:
            break

print 'Total subjects: ' + str(len(subj_ICDs))
for subject_stays in subj_ICDs:
    maxStays = max(len(subject_stays),maxStays)
print 'Most hospital stays: ' + str(maxStays)

with open('hospID-DATE.csv','rb') as hospfile:
    hosp_reader = csv.reader(hospfile)
    while True:
        try:
            row = hosp_reader.next()
            hadm_id = row[0]
            date = row[1]
            dateSplit = string.split(date, '/')
            month = int(dateSplit[0])
            if month in [1,3,5,7,8,10,12]:
                month = month * 31
            elif month in [4,6,9,11]:
                month = month * 30
            else:
                month = month * 28
            day = int(dateSplit[1])
            year = int(dateSplit[2]) * 365
            date = year + month + day
            for subj_id in subj_ICDs:
                if hadm_id in subj_ICDs[subj_id]:
                    subj_ICDs[subj_id][hadm_id][0] = date
        except:
            break

iterationCount = 0
total_entries = 0
total = len(subj_ICDs)
maxSize = 0
prevPercent = -1
db_filename = 'occurances.db'

if os.path.exists(db_filename):
    os.remove(db_filename)
conn = sqlite3.connect(db_filename)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE occurances
            (condition TEXT PRIMARY KEY,
            count INTEGER)''')

# For every subject that we have visiting the hospital
for subject_stays in subj_ICDs:

    if len(subj_ICDs[subject_stays]) > 1: # If they have more than 1 stay we can use their data
        numOverOne += 1 # Find how many we're visiting
        prevConditions = [] # Reset previous conditions since is a new patient
        patientStaysUnsorted = []
        patientStaysSorted = []
        allPrevConditions = []
        allConditionKeys = []

        # Sort the stays of this patient
        for hosp_stay in subj_ICDs[subject_stays]: # for each hospital stay
            curStay = subj_ICDs[subject_stays][hosp_stay] # Get the date and diagnoses
            patientStaysUnsorted.append(curStay)
        patientStaysSorted = patientStaysUnsorted
        for i in range(len(patientStaysSorted) - 1):
            for j in range(i+1,len(patientStaysSorted)):
                if patientStaysSorted[i] > patientStaysSorted[j]:
                    temp = patientStaysSorted[i]
                    patientStaysSorted[i] = patientStaysSorted[j]
                    patientStaysSorted[j] = temp
        for hosp_stay in subj_ICDs[subject_stays]: # For each hospital stay this patient has had
            curStay = subj_ICDs[subject_stays][hosp_stay] # Get the date and diagnoses
            newConditions = [] # Get ready to find what new/ongoing conditions they were diagonsed with this time
            iterableConditions = curStay[1:] # We just want data here, ie the conditions the patient has
            for rank, condition in iterableConditions: # Diagnosis is in form (rank,condition)
                newConditions.append(condition) # Add the current condition to his list of new conditions
                newConditionKeys = []
                #for prevConditionKey in allConditionKeys:
                #    prevConditionKey += "->" + condition
                #    newConditionKeys.append(prevConditionKey)
                #for newConditionKey in newConditionKeys:
                #    allConditionKeys.append(newConditionKey)
                # TODO Constrain comparisons to n-highest ranked conditions
                # TODO Compare to next n visits
                for prevConditionIteration in range(max(len(allPrevConditions)-MAX_DEGREE,0),len(allPrevConditions)): # for each previous visit they had
                    prevConditions = allPrevConditions[prevConditionIteration]
                    for prevCondition in prevConditions: # for every condition they had at this previous visit
                        if not prevCondition == condition: # As long as it's not the same condition
                            conditionKey = prevCondition + "->" + condition # Key is in form A->B, where A and B are the previous and new conditions, respectively
                            allConditionKeys.append(conditionKey)
                            cursor.execute("SELECT count FROM occurances WHERE condition=:condition", {"condition":conditionKey})
                            count = cursor.fetchone()
                            #print count
                            if count is not None: # If this progression has been seen before, increment its count
                                count = count[0]
                                count += 1
                                cursor.execute("UPDATE occurances SET count=:count WHERE condition=:condition", {"condition":conditionKey, "count":count})
                                #print '_________________________________________________________________________________________________REPEAT VALUE DOES IT CRASH?'
                            else: # Otherwise add it to the dictionary with initial count of 1
                                count = 1
                                cursor.execute("INSERT INTO occurances(condition, count) VALUES(:condition, :count)", {"condition":conditionKey, "count":count})
                                total_entries += 1

                            newConditions.append(conditionKey)
                            #if len(conditionKey) > 13:
                            #    print conditionKey
                    if len(allConditionKeys) > maxSize and INFO_DEBUG:
                        print 'Subject stay:', subject_stays
                        print 'Total stays:', len(subj_ICDs[subject_stays])
                        print 'Number of conditions:', len(iterableConditions)
                        print 'Previous conditions:', len(allPrevConditions)
                        print 'All previous:', len(prevConditions)
                        print 'Hospital stay:', hosp_stay
                        print '-----------------'
                        print 'allPrevConditions length:', len(allPrevConditions)
                        print 'Size of allPrevConditions:', str(sys.getsizeof(allPrevConditions) / 1000000) + " MB"
                        print 'newConditions length:', len(newConditions)
                        print 'Size of newConditions:', str(sys.getsizeof(newConditions) / 1000000) + " MB"
                        print 'allConditionKeys length:', len(allConditionKeys)
                        print 'Size of allConditionKeys:', str(sys.getsizeof(allConditionKeys) / 1000000) + " MB"
                        print '-----------------'
                        print 'Size of database:', str(os.path.getsize(db_filename) / 1000000) + " MB"
                        print '*******************************************************************************'
                        maxSize = max(maxSize, len(allConditionKeys))
            allPrevConditions.append(newConditions) # For the next visit, these new conditions will be the previous ones
            #print str(hosp_stay) + ": " + str(len(allPrevConditions))
    iterationCount += 1
    percentDone = iterationCount / float(total) * 100
    if int(percentDone) > prevPercent and PERCENT_DEBUG:
        print str(int(percentDone)) + "%\t\tSize of database:", str(os.path.getsize(db_filename) / 1000000) + " MB\t\tEntries:" + str(total_entries)
        prevPercent = percentDone
    conn.commit()

print "Running time: " + str(int(time.time() - startTime)) + "s"

conn.close()

#TODO get n-most frequent progressions
#TODO learn to sort by column in excel
with open('output.csv','wb') as outputCSV:
    outputWriter = csv.writer(outputCSV)