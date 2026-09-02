import tkinter as tk

from herdsim.ui.ui_utils import suppress_focus_rings


def test_buttons_and_scales_cannot_take_focus(root):
    frame = tk.Frame(root)
    nested = tk.Frame(frame)
    button = tk.Button(nested, text="sheep")
    scale = tk.Scale(nested)
    radio = tk.Radiobutton(nested, text="Wrap")
    entry = tk.Entry(nested)

    suppress_focus_rings(frame)

    for widget in (button, scale, radio):
        assert str(widget.cget("takefocus")) in ("0", "")
        assert int(widget.cget("highlightthickness")) == 0
    frame.destroy()


def test_entry_keeps_focus_so_typing_still_works(root):
    frame = tk.Frame(root)
    entry = tk.Entry(frame)
    suppress_focus_rings(frame)
    assert str(entry.cget("takefocus")) not in ("0",)
    frame.destroy()
