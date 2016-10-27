import csv,string,time,hashlib
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

uniqueConditions = []
causes = {}

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
        previousConditions = []
        for hosp_stay in subj_ICDs[subject_stays]: # For each hospital stay this patient has had
            curStay = subj_ICDs[subject_stays][hosp_stay] # Get the date and diagnoses
            newConditions = [] # Get ready to find what new/ongoing conditions they were diagonsed with this time
            iterableConditions = curStay[1:] # We just want data here, ie the conditions the patient has
            for rank, condition in iterableConditions: # Diagnosis is in form (rank,condition)
                newConditions.append(condition) # Add the current condition to his list of new conditions
                for prevCondition in prevConditions: # for every condition they had at this previous visit
                    if not prevCondition == condition: # As long as it's not the same condition
                        if prevCondition in causes:
                            if condition in causes[prevCondition]:
                                causes[prevCondition][condition] += 1
                            else:
                                #causes[prevCondition] = {}
                                causes[prevCondition][condition] = 1
                        else:
                            causes[prevCondition] = {}
                            causes[prevCondition][condition] = 1
            prevConditions = newConditions

    iterationCount += 1
    percentDone = iterationCount / float(total) * 100
    if int(percentDone) > prevPercent and PERCENT_DEBUG:
        print str(int(percentDone)) + "%"
        prevPercent = percentDone

print 'Size: ' + str(len(causes))

for key in causes:
    print key, causes[key]
