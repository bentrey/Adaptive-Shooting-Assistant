import tkinter as tk
from tkinter import filedialog as fd
from tkinter import LEFT,RIGHT,BOTH,TOP,BOTTOM
from speech.commands import Commands
from speech.tts import speak
from dialogs import WindowSettings, WindowBluetooth, WindowAbout
from util.wifi import have_internet



PROGRAM_NAME = " Adaptive Basketball Coach "
VERBOSE_HELP = False

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("640x480")
        self.title(PROGRAM_NAME)

        # Create menu bar
        menu = tk.Menu(self)

        # top level menus
        file_menu = tk.Menu(menu, tearoff=0)
        edit_menu = tk.Menu(menu, tearoff=0)
        about_menu = tk.Menu(menu, tearoff=0)

        menu.add_cascade(menu=file_menu, label='File')
        menu.add_cascade(menu=edit_menu, label='Edit')
        menu.add_cascade(menu=about_menu, label='About')

        # add File menu options
        file_menu.add_command(label='Capture data', command=self.capture_callback)
        file_menu.add_command(label='Load data', command=self.load_callback)
        file_menu.add_command(label='Save data', command=self.save_callback)
        file_menu.add_command(label='Pair Bluetooth', command=self.pair_callback)
        file_menu.add_command(label='Exit', command=self.destroy)

        # add Edit menu options
        edit_menu.add_command(label='Settings', command=self.settings_callback)

        # add About menu options
        about_menu.add_command(label='About', command=self.about_callback)
        about_menu.add_command(label='Help', command=self.help_callback)

        self.config(menu=menu)

        # add buttons
        self.capture_btn = tk.Button(self, text="Capture", command=self.capture_callback, fg="green", font='Helvetica 14 bold')
        self.capture_btn.pack(side=BOTTOM,fill=BOTH)

        self.pair_btn = tk.Button(self, text="Pair sensor", command=self.pair_callback, fg="blue", font='Helvetica 14 bold')
        self.pair_btn.pack(side=BOTTOM,fill=BOTH)


        # Create labelFrame
        self.grpData = tk.LabelFrame(self, padx=15, pady=10, text="Output")
        self.grpData.pack(fill=tk.BOTH, padx=10, pady=5)
        self.scroll_x = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.scroll_y = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.lblOutput = tk.Text(self.grpData,
                                 xscrollcommand=self.scroll_x.set,
                                 yscrollcommand=self.scroll_y.set)
        self.lblOutput.insert(tk.END, PROGRAM_NAME.strip() + " ready...\n")
        self.lblOutput.insert(tk.END, "Click on the capture button to start\n")
        self.lblOutput.pack()

        # check for internet connectivity
        self.have_internet = have_internet()

        # initialize our speech recognition
        self.speech_commands = Commands(have_internet)
        self.tts = speak(have_internet)

        self.capture_status = CaptureStatus()

    def capture_callback(self):
        if VERBOSE_HELP:
            self.speech_commands.spkResultList()
        self.tts.speak("Starting data capture.")
        word = self.speech_commands.startCapture()
        self.processCommand(word)

    def processCommand(self, word):
        self.lblOutput.insert(tk.END, "Processing command:" + word + "\n")
        if word == "capture":
            if (not self.capture_status):
                self.tts.speak("Please record your result first")
                self.speech_commands.spkResultList()
                self.capture_status = True;
            else:
                self.tts.speak(f"Ready to capture")
                self.capture_status = True;


        elif word == "stop":
            self.lblOutput.insert(tk.END, "Processing command:" + word + "\n")
            pass
        elif word == "save":
            pass
        elif word == "help":
            self.speech_commands.spkResultList()
        elif word == "exit":
            self.tk.destroy()
        elif word == "left":
            self.tts.speak(f"Data saved as {word}")
        elif word == "right":
            self.tts.speak(f"Data saved as {word}")
        elif word == "short":
            self.tts.speak(f"Data saved as {word}")
        elif word == "long":
            self.tts.speak(f"Data saved as {word}")
        elif word == "make":
            self.tts.speak("Nice shot!")
            self.tts.speak(f"Data saved as {word}")


    def load_callback(self):
        filetypes = (("CSV", "*.csv"),
                     ("Text", "*.txt"),
                     ("All files", "*"))
        filename = fd.askopenfilename(title="Open file", initialdir="/",
                                      filetypes=filetypes)
        if filename:
            self.lblOutput.insert(tk.END, f"Loading data from {filename}\n")


    def save_callback(self):
        #contents = self.text.get(1.0, tk.END)
        contents = "test\n"
        new_file = fd.asksaveasfile(title="Save file", defaultextension=".csv",
                                    filetypes=(("CSV", "*.csv"),))
        if new_file:
            new_file.write(contents)
            new_file.close()
            self.lblOutput.insert(tk.END, f"Saved to {new_file.name}\n")


    def pair_callback(self):
        # start bluetooth pairing
        window = WindowBluetooth(self)
        window.grab_set()

    def settings_callback(self):
        self.open_window()

    def open_window(self):
        window = WindowSettings(self)
        window.grab_set()

    def help_callback(self):
        self.speech_commands.spkCommandList()

    def about_callback(self):
        window = WindowAbout(self)
        window.grab_set()



class CaptureStatus():
    def __init__(self):
        self.isCapturing = False;


class AppSettings():
    #varDebug = tk.IntVar()
    #varVerbose = tk.IntVar()

    def __init__(self):
        pass

if __name__ == "__main__":
    app = App()
    app.mainloop()
