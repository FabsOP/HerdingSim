import tkinter as tk
from tktooltip import ToolTip

class BorderHandler(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#F5FBEF")
        #Border Handling section
        tk.Label(parent, text="Border Handling", bg="#F5FBEF", font = ("Comic Sans MS", 9, "bold"), fg="#4C6B32").pack(pady=10)
        borderSettingsFrame = tk.Frame(parent, bg="#F5FBEF")
        borderSettingsFrame.pack()
        
        # Radio buttons for border handling
        self.borderVar = tk.StringVar(value="Wrap")
        wrapRadio = tk.Radiobutton(borderSettingsFrame, width=6, text="Wrap", variable=self.borderVar, value="Wrap", bg="#E2F0D9", fg="#4C6B32", font=("Comic Sans MS", 8, "bold"), activebackground="#C1E1C1", activeforeground="#4C6B32", selectcolor="#A9C46C")
        stopRadio = tk.Radiobutton(borderSettingsFrame, width=6, text="Bounce", variable=self.borderVar, value="Bounce", bg="#E2F0D9", fg="#4C6B32", font=("Comic Sans MS", 8, "bold"), activebackground="#C1E1C1", activeforeground="#4C6B32", selectcolor="#A9C46C")
        followRadio = tk.Radiobutton(borderSettingsFrame, width=6, text="Follow", variable=self.borderVar, value="Follow", bg="#E2F0D9", fg="#4C6B32", font=("Comic Sans MS", 8, "bold"), activebackground="#C1E1C1", activeforeground="#4C6B32", selectcolor="#A9C46C") #wall following
        killRadio = tk.Radiobutton(borderSettingsFrame, width=6, text="Void", variable=self.borderVar, value="Void", bg="#E2F0D9", fg="#4C6B32", font=("Comic Sans MS", 8, "bold"), activebackground="#C1E1C1", activeforeground="#4C6B32", selectcolor="#A9C46C")
        
        wrapRadio.grid(row=0, column=0, padx=10, pady=7)
        stopRadio.grid(row=0, column=1, padx=10, pady=7)
        followRadio.grid(row=1, column=0, padx=10, pady=7)
        killRadio.grid(row=1, column=1, padx=10, pady=7)
        
        ToolTip(wrapRadio, msg="Animals reappear on the opposite side", delay=1, bd=1, font=("Comic Sans MS", 8, "bold"), bg="#E2F0D9", fg="#4C6B32")
        ToolTip(stopRadio, msg="Animals cannot cross the terrain edge", delay=1, bd=1, font=("Comic Sans MS", 8, "bold"), bg="#E2F0D9", fg="#4C6B32")
        ToolTip(killRadio, msg="Animals die if they reach the terrain edge", delay=1, bd=1, font=("Comic Sans MS", 8, "bold"), bg="#E2F0D9", fg="#4C6B32")
        ToolTip(followRadio, msg="Animals follow the terrain edge", delay=1, bd=1, font=("Comic Sans MS", 8, "bold"), bg="#E2F0D9", fg="#4C6B32")