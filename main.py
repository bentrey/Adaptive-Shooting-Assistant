import time

from coach.get_motion import *
from coach.get_feedback import *
from coach.get_suggestion import *
from coach.shared_variables import *

def __main__():

    global continue_variable
    global connection_state
    global connection_lock
    global speaker
    global speaker_lock
    global command
    global command_lock
    global shots
    global makes
    was_connected = False

    #creating threads
    motion = threading.Thread(target=get_motion)
    suggestion = threading.Thread(target=get_suggestion)
    sound = threading.Thread(target=get_feedback)

    #running threads
    motion.start()
    suggestion.start()
    sound.start()

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
        if connection_state == 1:
            #asking for user input
            choice = 0
            while not choice in [1,2]:
                choice = int(input('\n\nShots:'+str(shots)+' '+'\nMakes:'+\
                str(makes)+'\n\nPlease make a selection.\n\t1) Record Shot'+\
                '\n\t2) Exit'))
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

if __name__ == "__main__":
    __main__()