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


def test_frame_borders_survive(root):
    frame = tk.Frame(root)
    bordered = tk.Frame(frame, highlightbackground="#4C6B32", highlightthickness=2)
    label = tk.Label(frame, highlightthickness=3)
    button = tk.Button(frame)

    suppress_focus_rings(frame)

    assert float(bordered.cget("highlightthickness")) == 2, "frame border was wiped"
    assert float(label.cget("highlightthickness")) == 3, "label border was wiped"
    assert int(button.cget("highlightthickness")) == 0
    frame.destroy()


def test_real_ui_frames_keep_their_borders(root):
    from herdsim.ui.controller import Controller
    outer = tk.Frame(root)
    controller = Controller(outer)
    before = float(controller.cget("highlightthickness"))
    suppress_focus_rings(outer)
    assert float(controller.cget("highlightthickness")) == before > 0
    outer.destroy()
