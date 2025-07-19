import tkinter as tk
from tkinter import ttk


class MediaController(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, background="#D9E4D3", bd=5, highlightbackground="#4C6B32", highlightthickness=1.5)
        self.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="sew")  # Less top padding
        
        self.isPaused = False
        
        self.dtMultiplier = 1
        
        self.state = "running" #["running", "forward", "fast-forward", "rewind", "fast-rewind"]
        self.rewindUsable = True
        
        # Load your icons
        self.pauseIcon = tk.PhotoImage(file="icons/pause.png")
        self.playIcon = tk.PhotoImage(file="icons/play.png")

        # Configure grid to center buttons
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=1)

        style = ttk.Style()
        
                # Normal button style
        style.configure("Nature.TButton",
                background="#8CBF3D",
                foreground="#FEFAE0",
                font=("comic-sans", 9, "bold"),
                borderwidth=2,
                focusthickness=0,
                highlightthickness=0,
                relief="raised")
        style.map("Nature.TButton",
              background=[("active", "#A5D16C"), ("!active", "#8CBF3D")],
              foreground=[("active", "#FEFAE0"), ("!active", "#FEFAE0")])

        # Active (selected) button style
        style.configure("Active.TButton",
                background="black",
                foreground="#FEFAE0",
                font=("comic-sans", 9, "bold"),
                borderwidth=2,
                focusthickness=0,
                highlightthickness=0,  
                relief="raised")
        style.map("Active.TButton",
              background=[("active", "#333333"), ("!active", "black")],
              foreground=[("active", "#FEFAE0"), ("!active", "#FEFAE0")])


        # Add 5 buttons in center columns with nature colors
        self.btn1 = ttk.Button(self, text="Rewind (x4)", command=self.fastRewind, style="Nature.TButton", takefocus=False)
        self.btn2 = ttk.Button(self, text="Rewind", command=self.rewind, style="Nature.TButton", takefocus=False)
        self.btn3 = ttk.Button(self, image=self.pauseIcon, command=self.pausePlay, style="Nature.TButton", takefocus=False)
        self.btn4 = ttk.Button(self, text="Forward (x2)", command=self.fastForward2x, style="Nature.TButton", takefocus=False)
        self.btn5 = ttk.Button(self, text="Forward (x4)", command=self.fastForward4x, style="Nature.TButton", takefocus=False)

        self.btn1.grid(row=0, column=0)
        self.btn2.grid(row=0, column=1)
        self.btn3.grid(row=0, column=2)
        self.btn4.grid(row=0, column=3)
        self.btn5.grid(row=0, column=4)
        
        # remove focus from buttons after click
        for btn in [self.btn1, self.btn2, self.btn3, self.btn4, self.btn5]:
            btn.bind("<FocusIn>", lambda e: self.focus_set())
        
    def pausePlay(self):
        if not self.rewindUsable and self.isPaused:
            self.unFreezeRewind()
        
        # Temporarily disable button to prevent double clicks
        self.btn3.config(state="disabled")
        self.after(100, lambda: self.btn3.config(state="normal"))  # re-enable after 100ms
        
        
        self.isPaused = not self.isPaused
        
        if self.isPaused:
            self.btn3.config(image=self.playIcon)
            print("Simulation paused")
        else:
            self.btn3.config(image=self.pauseIcon)
            print("Simulation running")

    def fastForward2x(self):
        if self.dtMultiplier in [1,4]:
            self.state = "forward"
            print("Speed: x2")
            self.dtMultiplier = 2
            #set active style
            self.btn4.config(style="Active.TButton")
            #deactivate other button styles
            self.btn1.config(style="Nature.TButton")
            self.btn2.config(style="Nature.TButton")
            self.btn5.config(style="Nature.TButton") 
        else:
            self.dtMultiplier = 1
            self.state = "running"
            self.btn4.config(style="Nature.TButton")
    
    def fastForward4x(self):
        if self.dtMultiplier in [1,2]:
            self.state = "fast-forward"
            print("Speed: x4")
            self.dtMultiplier = 4
            #set active style
            self.btn5.config(style="Active.TButton")
            #deactivate other button styles
            self.btn1.config(style="Nature.TButton")
            self.btn2.config(style="Nature.TButton")
            self.btn4.config(style="Nature.TButton") 
        else:
            self.dtMultiplier = 1
            self.btn5.config(style="Nature.TButton")
            
    def rewind(self):
        if not self.rewindUsable:
            return
        if self.state in ["running", "forward", "fast-forward", "fast-rewind"]:
            self.dtMultiplier = 1
            self.state = "rewind"
            print("Rewinding")
            # Set active style for rewind button
            self.btn2.config(style="Active.TButton")
            # Deactivate other button styles
            self.btn1.config(style="Nature.TButton")
            self.btn4.config(style="Nature.TButton")
            self.btn5.config(style="Nature.TButton")
        else:
            self.dtMultiplier = 1
            self.state = "running"
            print("Simulation running at normal speed")
            self.btn2.config(style="Nature.TButton")
            
    
    def fastRewind(self):
        if not self.rewindUsable:
            return
        
        if self.state in ["running", "forward", "fast-forward", "rewind"]:
            self.dtMultiplier = 1
            self.state = "fast-rewind"
            print("Fast Rewinding at x4 speed")
            # Set active style for fast rewind button
            self.btn1.config(style="Active.TButton")
            # Deactivate other button styles
            self.btn2.config(style="Nature.TButton")
            self.btn4.config(style="Nature.TButton")
            self.btn5.config(style="Nature.TButton")
        else:
            self.dtMultiplier = 1
            self.state = "running"
            print("Simulation running at normal speed")
            self.btn1.config(style="Nature.TButton")
            
    
    def freezeRewind(self):
        self.rewindUsable = False
        
    def unFreezeRewind(self):
        self.rewindUsable = True