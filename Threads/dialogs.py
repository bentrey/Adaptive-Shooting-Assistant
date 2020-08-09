import tkinter as tk
#import bluetooth.bt_win as btwin


class WindowSettings(tk.Toplevel):
    '''
    Modal dialog class
    '''

    def __init__(self, parent):
        super().__init__(parent)
        self.geometry("320x200")
        self.varDebug = tk.IntVar()
        self.varVerbose = tk.IntVar()
        self.lblOutput = tk.Label(self, text="Adjust Settings")
        self.lblOutput.pack()
        self.cb = tk.Checkbutton(self, text="Enable debug", variable=self.varDebug, command=self.print_value)
        self.cb = tk.Checkbutton(self, text="Verbose help", variable=self.varVerbose, command=self.print_value)
        self.cb.pack()
        self.button = tk.Button(self, text="Close", command=self.destroy)
        self.label.pack(padx=20, pady=20)
        self.button.pack(pady=5, ipadx=2, ipady=2)

    def print_value(self):
        print(self.varDebug.get())


class WindowBluetooth(tk.Toplevel):
    '''
    Modal dialog class
    '''

    def __init__(self, parent):
        super().__init__(parent)
        self.list = tk.Listbox(self)
        self.list.insert(0, "device 1")
        self.pair_btn = tk.Button(self, text="Pair selection", command=self.pair_selection, fg="blue", font='Helvetica 14 bold')
        self.list.pack()
        self.pair_btn.pack(fill=tk.BOTH)

    def pair_selection(self):
        selection = self.list.curselection()
        print(selection)



class WindowAbout(tk.Toplevel):
    '''
    Modal dialog class
    '''

    def __init__(self, parent):
        super().__init__(parent)
        self.geometry("250x120")
        self.grpData = tk.LabelFrame(self, padx=5, pady=5, text="About")
        self.grpData.pack(fill=tk.BOTH, padx=10, pady=5)
        self.lblOutput = tk.Label(self.grpData, text="Adaptive Basketball Coach\nDGMS14 Summer 2020 Final Project")
        self.lblOutput.pack()
        self.button = tk.Button(self, text="Close", command=self.destroy)
        self.button.pack(pady=5, ipadx=2, ipady=2)

