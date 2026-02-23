import tkinter as tk

N = 50  # 50×50 rács

def redraw(event=None):
    canvas.delete("all")  # töröljük a régi rajzot
    
    # Az aktuális canvas mérete alapján számoljuk ki a cella méretet
    cell_size = min(canvas.winfo_width(), canvas.winfo_height()) / N
    
    for i in range(N):
        for j in range(N):
            x1 = j * cell_size
            y1 = i * cell_size
            x2 = x1 + cell_size
            y2 = y1 + cell_size
            
            canvas.create_rectangle(
                x1, y1, x2, y2,
                fill="white",
                outline="gray70",
                width=1 if cell_size > 6 else 0   # nagyon kicsinél eltűnik a vonal
            )

root = tk.Tk()
root.title("50×50 – átméretezhető")
root.geometry("600x600")           # kezdő méret

canvas = tk.Canvas(root, bg="#111", highlightthickness=0)
canvas.pack(fill="both", expand=True)

# Amikor az ablak átméreteződik → újrarajzoljuk
canvas.bind("<Configure>", redraw)

# Első rajzolás (indításkor)
root.after(50, redraw)   # kis késleltetés, hogy a canvas már létezzen

root.mainloop()