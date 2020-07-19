def get_feedback():
    global sound
    global sound_lock
    while True:
        if sound == 1:
            sound_lock.acquire()
            os.system('omxplayer /sounds/connecting.mp3')
            sound = 0
            sound_lock.release()
        elif  sound == 2:
            sound_lock.acquire()
            os.system('omxplayer /sounds/connected.mp3')
            sound = 0
            sound_lock.release()
        elif  sound == 3:
            sound_lock.acquire()
            os.system('omxplayer /sounds/followThrough.mp3')
            sound = 0
            sound_lock.release()
        elif  sound == 4:
            sound_lock.acquire()
            os.system('omxplayer /sounds/useYourLegs.mp3')
            sound = 0
            sound_lock.release()
        time.sleep(0.1)

def wait_for_speaker():
    while sound != 0:
        time.sleep(0.1)