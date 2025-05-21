import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo

############# MAIN WINDOW SETUP ############
root = tk.Tk()
root.title("My app")
rootW = 800
rootH = 500
sWidth = root.winfo_screenwidth()
sHeight = root.winfo_screenheight()

root.resizable(False, False)
root.geometry(f"800x500+{(sWidth-rootW)//2}+{(sHeight - rootH)//2}")
root.attributes("-alpha", 0.9)
root.attributes("-topmost", 1)
root.iconbitmap("./sheep-32.ico")

############ ADD LABEL ############
img = tk.PhotoImage(file="logo.png")
msg = ttk.Label(root, text="Hello, World!", anchor=tk.CENTER, font=("Arial",12), image=img, compound="top")
msg.pack()

############ ADD BUTTON ############
def clickMe(event):
    print("Button clicked!")

def log(event):
    print(event)
    
## Event binding   
btn = ttk.Button(root, text="Click me!")
btn.bind("<Return>", clickMe)
btn.bind("<Return>", log, add="+")
btn.focus()
btn.pack()

############# Disabled btn #################
disabledBtn = ttk.Button(root, text="Disabled", state="disabled")
disabledBtn.pack()

activateBtn = ttk.Button(root, text="Activate", command=lambda: disabledBtn.state(["!disabled"]))
activateBtn.pack()


quitBtn = ttk.Button(root, text= "Quit", command= lambda: root.quit())
quitBtn.pack(expand=True)

###### Downlooad btn ######
def download():
    showinfo(title="Status", message="Download started!")

dwnloadicon = tk.PhotoImage(file="download.png")
downloadBtn = ttk.Button(root, image=dwnloadicon, command=download, text="Download", compound="left")
downloadBtn.pack(ipadx=10, ipady=10, expand=True)

text = tk.StringVar()    
textbox = ttk.Entry(root, textvariable=text)
textbox.pack(expand=True)

textbox.bind("<Any-KeyPress>", lambda e: print(text.get()))
textbox.focus()

pwText = tk.StringVar()
password = ttk.Entry(root, show="*", textvariable=pwText)
password.pack(expand=True, fill="x")

root.mainloop()