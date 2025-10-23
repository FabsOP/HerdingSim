import tkinter as tk
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from path_utils import resource_path

class MainMenu(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HerdSim")
        self.config(background="#F5FBEF")  # Match controller background
        self.win_width = 300
        self.win_height = 240
        self.geometry(f"{self.win_width}x{self.win_height}")
        self.resizable(0, 0)

        # Logo
        logo = tk.PhotoImage(file=resource_path("icons/logo.png"))
        logoLabel = tk.Label(self, image=logo, background="#F5FBEF")
        logoLabel.image = logo  # Keep reference
        logoLabel.pack(pady=(18, 0))  # Add some top padding

        # Logo Text
        logoText = tk.Label(
            self,
            text="HerdSim",
            font=("Comic Sans MS", 16, "bold"),
            fg="#FF0000",
            bg="#F5FBEF"
        )
        logoText.pack(pady=(2, 10))

        # Play button
        playBtn = tk.Button(
            self,
            text='Play',
            width=25,
            bg="#E2F0D9",
            fg="#4C6B32",
            font=("Comic Sans MS", 10, "bold"),
            activebackground="#C1E1C1",
            activeforeground="#4C6B32",
            borderwidth=2,
            relief="raised",
            command=self.destroy
        )
        playBtn.pack(pady=5)

        # Exit button
        exitBtn = tk.Button(
            self,
            text='Exit',
            width=25,
            bg="#E2F0D9",
            fg="#4C6B32",
            font=("Comic Sans MS", 10, "bold"),
            activebackground="#C1E1C1",
            activeforeground="#4C6B32",
            borderwidth=2,
            relief="raised",
            command=sys.exit
        )
        exitBtn.pack(pady=5)

        # Bind the close event to the destroy method
        self.protocol("WM_DELETE_WINDOW", sys.exit)
        self.center_window()
        self.iconbitmap(resource_path("icons/sheep.ico"))
        self.mainloop()

    def center_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (self.win_width // 2)
        y = (screen_height // 2) - (self.win_height // 2)
        self.geometry(f"+{x}+{y}")