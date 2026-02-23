import tkinter as tk

root = tk.Tk()
root.title("50x50")

canvas = tk.Canvas(root, width=500, height=500)
canvas.pack()

for i in range(50):
    for j in range(50):
        x = j * 10
        y = i * 10
        canvas.create_rectangle(x, y, x+10, y+10, fill="white", outline="gray")

root.mainloop()