import tkinter as tk
from tkinter import ttk


class MediaController(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, background="#D9E4D3", bd=5, highlightbackground="#4C6B32", highlightthickness=1.5)
        self.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="sew")  # Less top padding
        
        self.isPaused = False
        
        self.dtMultiplier = 1
        
        # Load your icons
        self.pauseIcon = tk.PhotoImage(file="icons/pause.png")
        self.playIcon = tk.PhotoImage(file="icons/play.png")

        # Configure grid to center buttons
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=1)

        font = ("comic-sans", 9, "bold")

        # Add 3 buttons in center columns with nature colors
        self.btn1 = tk.Button(self, text="Rewind (x4)", bg="#8CBF3D", fg="#FEFAE0", font=font, bd=0)
        self.btn2 = tk.Button(self, text="Rewind (x2)", bg="#8CBF3D", fg="#FEFAE0", font=font, bd=0)
        self.btn3 = tk.Button(self, image=self.pauseIcon, bg="#A5D16C", fg="#FEFAE0", font=font, bd=0, activebackground="black", command= self.pausePlay)
        self.btn4 = tk.Button(self, text="Forward (x2)", bg="#8CBF3D", fg="#FEFAE0", font=font, bd=0, command=self.fastForward2x )
        self.btn5 = tk.Button(self, text="Forward (x4)", bg="#8CBF3D", fg="#FEFAE0", font=font, bd=0, command=self.fastForward4x)

        self.btn1.grid(row=0, column=0)
        self.btn2.grid(row=0, column=1)
        self.btn3.grid(row=0, column=2)
        self.btn4.grid(row=0, column=3)
        self.btn5.grid(row=0, column=4)
        
    def pausePlay(self):
        # Temporarily disable button to prevent double clicks
        self.btn3.config(state="disabled")
        self.after(100, lambda: self.btn3.config(state="normal"))  # re-enable after 100ms
        
        
        self.isPaused = not self.isPaused
        
        if self.isPaused:
            self.btn3.config(image=self.playIcon)
        else:
            self.btn3.config(image=self.pauseIcon)

    def fastForward2x(self):
        if self.dtMultiplier in [1,4]:
            print("Speed: x2")
            self.dtMultiplier = 2
            #set active style
            self.btn4.config(bg="black")
            #deactivate other button styles
            self.btn1.config(bg="#8CBF3D")
            self.btn2.config(bg="#8CBF3D")
            self.btn5.config(bg="#8CBF3D") 
        else:
            print("Speed: Normal")
            self.dtMultiplier = 1
            self.btn4.config(bg="#8CBF3D")
    
    def fastForward4x(self):
        if self.dtMultiplier in [1,2]:
            print("Speed: x4")
            self.dtMultiplier = 4
            #set active style
            self.btn5.config(bg="black")
            #deactivate other button styles
            self.btn1.config(bg="#8CBF3D")
            self.btn2.config(bg="#8CBF3D")
            self.btn4.config(bg="#8CBF3D") 
        else:
            print("Speed: Normal")
            self.dtMultiplier = 1
            self.btn5.config(bg="#8CBF3D")