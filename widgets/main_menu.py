import tkinter as tk
import sys

class MainMenu(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HerdSim")
        self.config(background="#ffffff")
        self.geometry("300x200")
        self.resizable(0, 0)
        
        L1 = tk.Label(self, text="Main Menu", background="#ffffff")
        L1.pack()
        
        #Logo 
        logo = tk.PhotoImage(file="logo.png")
        logoLabel = tk.Label(self, image=logo, background="#ffffff")
        logoLabel.pack()
        
        #Logo Text
        logoText = tk.Label(self, text="HerdSim", font=("Helvetica", 12, "bold"), fg="Red", bg="White")
        logoText.pack()
        
        #Play button
        button = tk.Button(self, text='Play', width=25, command=self.destroy)
        button.pack(pady=5)

        exitBtn = tk.Button(self, text='Exit', width=25, command=sys.exit)
        exitBtn.pack(pady=5)

        self.mainloop()