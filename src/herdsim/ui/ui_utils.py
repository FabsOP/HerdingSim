import tkinter as tk

#only these draw a dotted focus ring and steal key presses such as space
_FOCUS_RING = (tk.Button, tk.Radiobutton, tk.Checkbutton, tk.Scale)


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
            #frames and labels use highlightthickness for their visible border
            if isinstance(child, _FOCUS_RING):
                try:
                    child.configure(highlightthickness=0)
                except tk.TclError:
                    pass
        suppress_focus_rings(child)
