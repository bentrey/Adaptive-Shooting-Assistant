import time
from shared_variables import *

def get_feedback():
    global speaker
    global speaker_lock
    global continue_variable
    while continue_variable:
        if speaker == 1:
            speaker_lock.acquire()
            os.system('omxplayer /sounds/connecting.mp3')
            speaker = 0
            speaker_lock.release()
        elif  speaker == 2:
            sound_lock.acquire()
            os.system('omxplayer /sounds/connected.mp3')
            speaker = 0
            speaker_lock.release()
        elif  speaker == 3:
            speaker_lock.acquire()
            os.system('omxplayer /sounds/followThrough.mp3')
            speaker = 0
            speaker_lock.release()
        elif  speaker == 4:
            speaker_lock.acquire()
            os.system('omxplayer /sounds/useYourLegs.mp3')
            speaker = 0
            speaker_lock.release()
        elif  speaker == 5:
            speaker_lock.acquire()
            os.system('omxplayer /sounds/shoot.mp3')
            speaker = 0
            speaker_lock.release()
        time.sleep(0.1)

def wait_for_speaker():
    while speaker != 0:
        time.sleep(0.1)