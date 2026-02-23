import tkinter as tk

N = 50

def redraw(event=None):
    canvas.delete("all")
    
    # Aktuális ablakméret
    w = canvas.winfo_width()
    h = canvas.winfo_height()
    
    # Cellaméret: az ablak teljes szélességét és magasságát elosztjuk N-nel
    cell_w = w / N
    cell_h = h / N
    
    for i in range(N):
        for j in range(N):
            x1 = j * cell_w
            y1 = i * cell_h
            x2 = (j + 1) * cell_w
            y2 = (i + 1) * cell_h
            
            canvas.create_rectangle(
                x1, y1, x2, y2,
                fill="white",
                outline="gray70",
                width=1 if min(cell_w, cell_h) > 5 else 0
            )

root = tk.Tk()
root.title("50×50 – mindig kitölti, bármerre húzható")
root.geometry("600x600")

# Fontos: a canvas kitölti az egész ablakot
canvas = tk.Canvas(root, bg="black", highlightthickness=0)
canvas.pack(fill="both", expand=True)

# Átméretezéskor azonnal újrarajzol
canvas.bind("<Configure>", redraw)

# Első rajzolás (kicsit várunk, hogy a méret már meglegyen)
root.after(100, redraw)

root.mainloop()