import tkinter as tk

#widgets that draw a dotted focus ring and steal key presses such as space
_NO_FOCUS = (tk.Button, tk.Radiobutton, tk.Checkbutton, tk.Scale, tk.Label, tk.Frame)


def center_window(win, width, height, shift=30):
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2) - shift
    win.geometry(f"+{x}+{y}")


def suppress_focus_rings(widget):
    for child in widget.winfo_children():
        if not isinstance(child, (tk.Entry, tk.Text)):
            try:
                child.configure(takefocus=0)
            except tk.TclError:
                pass
            if isinstance(child, _NO_FOCUS):
                try:
                    child.configure(highlightthickness=0)
                except tk.TclError:
                    pass
        suppress_focus_rings(child)
