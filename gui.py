import tkinter as tk

N = 50

def redraw(event=None):
    canvas.delete("all")
    
    w = canvas.winfo_width()
    h = canvas.winfo_height()
    
    # Egyszerűen az ablak méretéhez igazítjuk – torzulhat
    cell_w = w / N
    cell_h = h / N
    
    for i in range(N):
        for j in range(N):
            x1 = j * cell_w
            y1 = i * cell_h
            x2 = x1 + cell_w
            y2 = y1 + cell_h
            
            canvas.create_rectangle(
                x1, y1, x2, y2,
                fill="white",
                outline="gray60",
                width=1 if min(cell_w, cell_h) > 4 else 0
            )

root = tk.Tk()
root.title("50×50 – kitölti az ablakot, torzulhat")
root.geometry("800x500")   # szándékosan nem négyzet

canvas = tk.Canvas(root, bg="black", highlightthickness=0)
canvas.pack(fill="both", expand=True)

canvas.bind("<Configure>", redraw)
root.after(50, redraw)   # első kirajzolás

root.mainloop()