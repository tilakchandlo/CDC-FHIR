from sklearn import datasets
from sklearn.naive_bayes import GaussianNB
import csv,string,re

COL_SEQ = -1
COL_DIAG = []
COL_AGEOFADMIT = -1

class Stay:
    def __init__(self,subject_id,hadm_id,sequence,code):
        self.subject_id = subject_id
        self.hadm_id = hadm_id
        self.sequence = sequence
        self.code = code

class Patient:
    def __init__(self,subject_id,gender,age,hadm_id,hospital_tos,height,weightFirst,weightMin,weightMax,conditions):
        self.subject_id = subject_id
        self.gender = gender
        self.age = age
        self.hospital_tos = hospital_tos
        self.hadm_id = hadm_id
        self.height = height
        self.weightFirst = weightFirst
        self.weightMin = weightMin
        self.weightMax = weightMax
        self.conditions = conditions

def calculate_age(born, died):
    if monthIndex(died[0]) < monthIndex(born[0]):
        return int(died[2]) - int(born[2]) - 1
    elif monthIndex(died[0]) == monthIndex(born[0]) and died[1] < born[1]:
        return int(died[2]) - int(born[2]) - 1
    return int(died[2]) - int(born[2])

def monthIndex(month):
    return {
        'January' : 1,
        'February' : 2,
        'March' : 3,
        'April' : 4,
        'May' : 5,
        'June' : 6,
        'July' : 7,
        'August' : 8,
        'September' : 9,
        'October' : 10,
        'November' : 11,
        'December' : 12,
    }[month]

mDict = {}
arr = []
mSubjects = {}

with open('CDC_ICU_Mortality.csv','rb') as ICUfile:
    ICUreader = csv.reader(ICUfile)
    headerRow = True
    for row in ICUreader:
        if not headerRow:
            subject_id = row[1]
            gender = row[2]
            dob = string.split(row[3],' ')
            dob[1] = string.replace(dob[1], ',', '')
            dod = string.split(row[4],' ')
            dod[1] = string.replace(dod[1], ',', '')
            #print dob,"........",dod
            age = calculate_age(dob,dod)
            hadm_Id = row[8]
            hospital_tos = row[15]
            height = row[31]
            weightFirst = row[32]
            weightMin = row[33]
            weightMax = row[34]
            conditions = row[-30:]
            mSubjects[subject_id] = Patient(subject_id,gender,age,hadm_Id,hospital_tos,height,weightFirst,weightMin,weightMax,conditions)
            #arr.append()
            print mSubjects[subject_id]
        else:
            headerRow = False

subj_ICDs = {}
fi = open('ICD9.csv', 'rb')
data = fi.read()
with open('ICD9.csv','rb') as ICD9file:
    ICD9reader = csv.reader(ICD9file)
    headerRow = True
    for row in ICD9reader:
        if not headerRow:
            subject_id = row[1]
            hadm_id = row[2]
            sequence = row[3]
            code = row[4]
            subj_ICDs[subject_id] = Stay(subject_id,hadm_id,sequence,code)
        else:
            headerRow = False












