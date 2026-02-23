import tkinter as tk

N = 50  # 50×50 rács

def redraw(event=None):
    canvas.delete("all")
    
    w = canvas.winfo_width()
    h = canvas.winfo_height()
    
    # A cella mérete a kisebbik oldalhoz igazodik → így marad négyzet
    cell_size = min(w, h) / N
    
    offset_x = (w - cell_size * N) / 2   # középre igazítás vízszintesen
    offset_y = (h - cell_size * N) / 2   # középre igazítás függőlegesen
    
    for i in range(N):
        for j in range(N):
            x1 = offset_x + j * cell_size
            y1 = offset_y + i * cell_size
            x2 = x1 + cell_size
            y2 = y1 + cell_size
            
            canvas.create_rectangle(
                x1, y1, x2, y2,
                fill="white",
                outline="gray60",
                width=1 if cell_size > 5 else 0
            )

root = tk.Tk()
root.title("50×50 – mindig négyzet, középre igazítva")
root.geometry("700x700")

canvas = tk.Canvas(root, bg="#0a0a0a", highlightthickness=0)
canvas.pack(fill="both", expand=True)

# Átméretezéskor újrarajzolás
canvas.bind("<Configure>", redraw)

# Első kirajzolás (indítás után kicsit várunk, hogy a méret már jó legyen)
root.after(100, redraw)

root.mainloop()