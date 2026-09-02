def center_window(win, width, height, shift=30):
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2) - shift
    win.geometry(f"+{x}+{y}")
