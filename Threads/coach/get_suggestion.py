import time
import pandas as pd
import numpy as np

from sklearn.linear_model import LogisticRegression

from coach.shared_variables import *

def get_suggestion():

    global continue_variable
    global command
    global command_lock
    global motion_data

#To do
#  Import data points in motion data
#  Add quadratic terms
#  Add more suggestions
#  If there is lots of data use K-Means to get relavent data


    while continue_variable:
        if command == 2:
            width = motion_data.shape()[1]
            rows = motion_data.shape()[0]
            followThroughIncrease = np.array((width-2)*[0])
            useYourLegsIncrease = np.array((width-2)*[0])
            suggestions = data_motion['suggestion'].to_numpy()
            followThroughs = suggestions.count('followThrough')
            useYourLegs = suggestions.count('useYourLegs')
            values = motion_data.drop(['make', 'suggestion'])
            for n in range(rows-1):
                if motion_data['suggestion'][n] == 'followThrough':
                    followThroughIncrease += values[[n+1]]/values[[n]]/followThroughs
                elif motion_data['suggestion'][n] == 'useYourLegs':
                    followThroughIncrease += values[[n+1]]/values[[n]]/useYourLegs
            X = motion_data.drop(['make','suggestion'])
            y = motion_data['make']
            clf = LogisticRegression().fit(X, y)
            last_values = motion_data.drop['make', 'suggestion'][[rows-1]]
            if clf.predict(last_values*followThroughIncrease) > \
                clf.predict(last_values*useYourLegsIncrease):
                speaker_lock.acquire()
                speaker = 4
                speaker_lock.release()
                motion_data_lock.acquire()
                motion_data['suggestion'][rows-1] = 'followThrough'
                motion_data_lock.release()
            else:
                speaker_lock.acquire()
                speaker = 5
                speaker_lock.release()
                motion_data_lock.acquire()
                motion_data['suggestion'][rows-1] = 'useYourLegs'
                motion_data_lock.release()
        else:
            time.sleep(0.1)