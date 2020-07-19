import sys
import os
import time
import datetime
import click
import pandas as pd
from scipy import integrate
from abc import abstractmethod
from threading import Thread

from blue_st_sdk.manager import Manager
from blue_st_sdk.manager import ManagerListener
from blue_st_sdk.node import NodeListener
from blue_st_sdk.feature import FeatureListener
from blue_st_sdk.features.audio.adpcm.feature_audio_adpcm import FeatureAudioADPCM

from sklearn.linear_model import LogisticRegression

from get_motion.py import *
from get_feedback.py import *
from get_suggestion.py import * 

connection_state = 3 #0 connecting, 1 connected, 2 disconnecting, 3 disconnected
connection_lock = threading.RLock()
command = #0 do nothing, 1 get shot data, 2 get suggestion
command_lock = threading.RLock()
data_columns = ['int_ax', 'ax_min', 'ax_max', 'int_ay', 'ay_min', \
                'ay_max', 'int_az', 'az_min', 'az_max', 'gyr_x_final', \
                'gyr_x_min', 'gyr_x_max', 'gyr_y_min', 'gyr_y_max', \
                'gyr_y_final', 'gyr_z_min', 'gyr_z_max', 'gyr_z_final', \
                'made','suggestion'] 
motion_data = pd.dataFrame([], columns = data_columns)
motion_data_lock = threading.RLock()
speaker = 0
speaker_lock = threading.RLock()
continue_variable = True
connection_tries = 10

def __main__():

    global connection_state
    global connection_lock
    global speaker
    global speaker_lock
    global command
    global command_lock
    global shots = 0
    global makes = 0
    was_connected = False

    #creating threads
    motion = threading.Thread(target=get_motion)
    suggestion = threading.Thread(target=get_suggestion)
    sound = threading.Thread(target=get_feedback)

    #running threads
    recongnize.start()
    suggestion.start()
    player.start()

    while continue_variable:
        ##connecting
        #telling the user the ble device is connecting
        if connection_state == 0:
            wait_for_speaker()
            speaker_lock.acquire()
            speaker = 1
            speaker_lock.release()
        #waiting for connection 
        tries = 0
        while connection_state !=1 and tries<connection_tries:
            tries += 1
            time.sleep(0.5)
        #telling the user they are connected if they weren't
        if connection_state == 1 and  not was_connected:
            wait_for_speaker()
            speaker_lock.acquire()
            speaker = 2
            speaker_lock.release()
            was_connected = True
        ##getting data
        if connected:
            #asking for user input
            choice = 0
            while not choice in [1,2]:
                choice = int(input('\n\nShots:'+str(shots)+' '+'\nMakes:'+\
                str(makes)+'\n\nPlease make a selection.\n\t1) Record Shot'+\
                '\n\t2) Exit')))
                if not choice in [1,2]:
                    sys.stdout('\n\nPlease select 1) or 2).')
            #recording data
            if choice == 1:
                while command != 0:
                    time.sleep(0.1)
                command_lock.acquire()
                command = 1
                command_lock.release()
                while command != 0:
                    time.sleep(0.1)
                #getting suggestion
                command_lock.acquire()
                command = 2
                command_lock.release()
                while command != 0:
                    time.sleep(0.1)
            else:
                continue_variable = False
__main__()