from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
import time

# TODO: put this class in a package
import speech_recognition as sr

class Commands:
    def __init__(self):
        # Words that sphinx should listen closely for. 0-1 is the sensitivity
        # of the wake word.
        self.keywords = [("capture", 1),  # start the capture of data
                         ("save", 1),     # save session
                         ("left", 1),
                         ("right", 1),
                         ("short", 1),
                         ("long", 1),
                         ("make", 1)]


    def callback(self, recognizer, audio):                          # this is called from the background thread
        try:
            speech_as_text = recognizer.recognize_sphinx(audio, keyword_entries=self.keywords)
            print(speech_as_text)
            #self.textlbl.set(speech_as_text)

            # Look for your "Ok Google" keyword in speech_as_text
            if "capture" in speech_as_text:
                self.start_capture()
            # process  other commands/actions
        except sr.UnknownValueError:
            print("Oops! Didn't catch that")

        try:
            print("You said " + recognizer.recognize(audio))  # received audio data, now need to recognize it
        except LookupError:
            print("Oops! Didn't catch that")


    def start_capture(self):
        print("Starting data capture...")
        # pair bluetooth
        # capture data
        # save data

    def start(self, textlbl):
        self.textlbl = textlbl
        self.r = sr.Recognizer()
        self.source = sr.Microphone()
        self.r.listen_in_background(self.source, self.callback)
        #time.sleep(1000000)


PROGRAM_NAME = " Adaptive Basketball Coach "

def build_menu():
    menubar = Menu(root)
    # top level menus
    file_menu = Menu(menubar, tearoff=0)
    edit_menu = Menu(menubar, tearoff=0)
    about_menu = Menu(menubar, tearoff=0)

    menubar.add_cascade(menu=file_menu, label='File')
    menubar.add_cascade(menu=edit_menu, label='Edit')
    menubar.add_cascade(menu=about_menu, label='About')

    # add File menu options
    file_menu.add_command(label='Capture data', accelerator='Ctrl+A', command=capture_callback, underline=1)
    file_menu.add_command(label='Load data', accelerator='Ctrl+L', command=load_callback, underline=0)
    file_menu.add_command(label='Save data', accelerator='Ctrl+S', command=save_callback, underline=0)
    file_menu.add_command(label='Pair Bluetooth', accelerator='Ctrl+P', command=pair_callback, underline=0)
    file_menu.add_command(label='Exit', accelerator='Ctrl+X', command=exit_callback, underline=1)

    # add Edit menu options
    edit_menu.add_command(label='Settings', accelerator='Ctrl+E', command=settings_callback, underline=1)

    # add About menu options
    about_menu.add_command(label='About')
    about_menu.add_command(label='Help')

    textlbl = StringVar()
    textlbl.set("")
    lblSpeech = Label(root, textvariable=textlbl, text='Speech:').grid(row=0,column=0)
    root.config(menu=menubar)

def capture_callback():
    speech_commands = Commands()
    speech_commands.start()

def load_callback():
    name = fd.askopenfilename()
    print(name)

def save_callback():
    name = fd.asksaveasfilename()
    print(name)

def pair_callback():
    name = fd.askopenfilename()
    print(name)

def settings_callback():
    pass

def exit_callback():
    root.destroy()

root = Tk()
root.geometry("640x480")
build_menu()

root.title(PROGRAM_NAME)

root.mainloop()
