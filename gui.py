import tkinter as tk

N = 50

_redraw_job = None

def redraw(event=None):
    global _redraw_job
    if _redraw_job is not None:
        root.after_cancel(_redraw_job)
    _redraw_job = root.after(30, _do_redraw)

def _do_redraw():
    global _redraw_job
    _redraw_job = None

    w = canvas.winfo_width()
    h = canvas.winfo_height()
    if w <= 1 or h <= 1:
        return

    canvas.delete("all")

    cell_w = w / N
    cell_h = h / N
    show_outline = min(cell_w, cell_h) > 5

    # Háttér egyetlen téglalappal
    canvas.create_rectangle(0, 0, w, h, fill="white", outline="")

    if show_outline:
        # Vízszintes vonalak
        for i in range(N + 1):
            y = i * cell_h
            canvas.create_line(0, y, w, y, fill="gray70")

        # Függőleges vonalak
        for j in range(N + 1):
            x = j * cell_w
            canvas.create_line(x, 0, x, h, fill="gray70")

root = tk.Tk()
root.title("RGP1")
root.geometry("600x600")

canvas = tk.Canvas(root, bg="white", highlightthickness=0)
canvas.pack(fill="both", expand=True)

canvas.bind("<Configure>", redraw)
root.after(100, _do_redraw)

root.mainloop()
