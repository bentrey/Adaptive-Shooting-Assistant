import speech_recognition as sr
from speech.tts import speak

class Commands:
    def __init__(self, have_internet):
        # Words that sphinx should listen closely for. 0-1 is the sensitivity
        # of the wake word.
        self.keywords = { "coach" : [("capture", 1),     # start the capture of data
                                      ("stop", 1),       # stop capture
                                      ("save", 1),       # save captured data points
                                      ("exit", 1),       # exit app
                                      ("help", 1)],      # get a list of commands
                        "result": [("left", 1),
                                      ("right", 1),
                                      ("short", 1),
                                      ("long", 1),
                                      ("make", 1)]
                          }

        # build a list of recognized word commands
        self.words = []
        c = self.keywords['coach']
        for k in c:
            self.words.append(k[0])
        c = self.keywords['result']
        for k in c:
            self.words.append(k[0])

        self.result = [("left", 1),
                       ("right", 1),
                       ("short", 1),
                       ("long", 1),
                       ("make", 1)]

        self.result_list = ["left", "right", "short", "long", "make"]

        self.feedback = {"ns" : "No suggestion",
                         "ft" : "Follow through",
                         "cw" : "Turn wrist",
                         "bl" : "Bend legs",
                         "ei" : "Elbow in",
                         "ss" : "Square shoulder",
                         "sf" : "Shoot faster",
                         "so" : "Shoot in one continuous motion"
                         }

        # initialize tts
        self.have_internet = have_internet
        self.tts = speak(have_internet)

        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()


    def spkCoachList(self):
        self.tts.speak("Use the following commands to perform the action.")
        c = self.keywords['coach']
        for k in c:
            self.tts.speak(k[0])


    def spkResultList(self):
        self.tts.speak("Speak one of the words below after you make your shot.")
        r = self.keywords['result']
        for k in r:
            self.tts.speak(k[0])


    def spkCommandList(self):
        self.tts.speak("List of commands.")
        self.spkCoachList()
        self.spkResultList()


    def recognize_speech_from_mic(self, recognizer, microphone):
        """Transcribe speech from recorded from `microphone`.

        Returns a dictionary with three keys:
        "success": a boolean indicating whether or not the API request was
                   successful
        "error":   `None` if no error occured, otherwise a string containing
                   an error message if the API could not be reached or
                   speech was unrecognizable
        "transcription": `None` if speech could not be transcribed,
                   otherwise a string containing the transcribed text
        """
        # check that recognizer and microphone arguments are appropriate type
        if not isinstance(recognizer, sr.Recognizer):
            raise TypeError("`recognizer` must be `Recognizer` instance")

        if not isinstance(microphone, sr.Microphone):
            raise TypeError("`microphone` must be `Microphone` instance")

        # adjust the recognizer sensitivity to ambient noise and record audio
        # from the microphone
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        # set up the response object
        response = {
            "success": True,
            "error": None,
            "transcription": None
        }

        # try recognizing the speech in the recording
        # if a RequestError or UnknownValueError exception is caught,
        #     update the response object accordingly
        try:
            if self.have_internet:
                response["transcription"] = recognizer.recognize_google(audio)
            else:
                response["transcription"] = recognizer.recognize_sphinx(audio)
        except sr.RequestError:
            # API was unreachable or unresponsive
            response["success"] = False
            response["error"] = "API unavailable"
        except sr.UnknownValueError:
            # speech was unintelligible
            response["error"] = "Unable to recognize speech"

        return response


    def startCapture(self):
        '''
        startCapture - initialize the SR libray and listen for commands
        :return: None
        '''

        # create recognizer and mic instances
        #self.recognizer = sr.Recognizer()
        #self.microphone = sr.Microphone()

        #self.recognizer.adjust_for_ambient_noise(self.microphone)
        #self.recognizer.listen_in_background(self.microphone, self.callback)

        done = False
        while (not done):
            self.tts.speak("Speak a command")
            guess = self.recognize_speech_from_mic(self.recognizer, self.microphone)
            if guess["transcription"]:
                word = guess["transcription"].lower()
                print(f"You said {word}")
                if word == 'help':
                    self.spkResultList()
                elif word in self.words:
                    print(f"Found word")
                    done=True
                else:
                    if not guess["success"]:
                        print("I didn't catch that. What did you say?\n")
                        self.tts.speak("I didn't catch that. Say help for a list of commands.")
        print(f"Done processing")
        return word




