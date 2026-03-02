#!/usr/bin/env python3
"""
Mars Rover Szimuláció
Használat: python mars_rover.py [időkeret_órában]
1 szimulációs óra = 10 valódi másodperc
"""

import tkinter as tk
import heapq
import math
import time
import threading
import sys
import os

# === Konstansok ===
K = 2                  # Energiaállandó
DAY_HOURS = 16         # Nappal hossza (óra)
NIGHT_HOURS = 8        # Éjszaka hossza (óra)
CHARGE_RATE = 10       # Töltés fél óránként nappal
MINING_COST = 2        # Bányászás fogyasztás fél óránként
STANDBY_COST = 1       # Standby fogyasztás
MAX_BATTERY = 100.0    # Max akkumulátor kapacitás

# Sebesség opciók (blokk/fél óra)
SPEED_SLOW   = 1
SPEED_NORMAL = 2
SPEED_FAST   = 3

# Vizualizáció
CELL = 12   # Pixel / cella
INFO_W = 230

COLORS = {
    '.': '#c8834a',
    '#': '#3a3a3a',
    'B': '#1a77ff',
    'Y': '#ffcc00',
    'G': '#11bb11',
    'S': '#ff5533',
    'collected': '#7a5530',
    'trail':     '#e09a60',
}


# ===========================================================
# Segédfüggvények
# ===========================================================

def parse_map(filename):
    grid = []
    start = None
    with open(filename) as f:
        for r, line in enumerate(f):
            row = [c.strip() for c in line.strip().split(',')]
            for c, cell in enumerate(row):
                if cell == 'S':
                    start = (r, c)
            grid.append(row)
    return grid, start


def heuristic(a, b):
    # Chebyshev-távolság (átlós mozgás = 1 lépés)
    return max(abs(a[0]-b[0]), abs(a[1]-b[1]))


def astar(grid, start, goal, rows, cols):
    """A* útkereső, átlós mozgással. Visszaad egy pozíció-listát."""
    if start == goal:
        return [start]
    heap = [(0, 0, start)]
    g = {start: 0}
    parent = {}
    cnt = 0
    while heap:
        _, _, cur = heapq.heappop(heap)
        if cur == goal:
            path = []
            while cur in parent:
                path.append(cur)
                cur = parent[cur]
            path.append(start)
            return path[::-1]
        r, c = cur
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r+dr, c+dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != '#':
                    ng = g[cur] + 1
                    nb = (nr, nc)
                    if ng < g.get(nb, 10**9):
                        g[nb] = ng
                        parent[nb] = cur
                        cnt += 1
                        heapq.heappush(heap, (ng + heuristic(nb, goal), cnt, nb))
    return None


def is_day(half_hour):
    """Meghatározza, hogy nappal van-e az adott félóránál."""
    return (half_hour // 2) % 24 < DAY_HOURS


def net_move(speed, half_hour):
    """Mozgás nettó energiaváltozása egy félóra alatt."""
    charge = CHARGE_RATE if is_day(half_hour) else 0
    return charge - K * speed * speed


def net_mine(half_hour):
    """Bányászás nettó energiaváltozása egy félóra alatt."""
    charge = CHARGE_RATE if is_day(half_hour) else 0
    return charge - MINING_COST


def travel_half_hours(dist, speed):
    return math.ceil(dist / speed) if dist > 0 else 0


# ===========================================================
# Útvonaltervező (mohó algoritmus)
# ===========================================================

def plan_route(grid, start, rows, cols, total_half_hours):
    """
    Mohó stratégia: mindig a legközelebbi elérhető ásványhoz megy,
    ha még vissza tud érni az indulóponthoz időben és energiával.
    """
    route = []
    sim_grid = [row[:] for row in grid]
    sim_pos = start
    sim_battery = MAX_BATTERY
    sim_t = 0

    # Összes ásvány megkeresése
    remaining = set()
    for r in range(rows):
        for c in range(cols):
            if sim_grid[r][c] in ('B', 'Y', 'G'):
                remaining.add((r, c))

    while remaining:
        best = None
        best_score = 10**9
        best_info = None

        for mineral in remaining:
            path_to = astar(sim_grid, sim_pos, mineral, rows, cols)
            if not path_to:
                continue
            path_from = astar(sim_grid, mineral, start, rows, cols)
            if not path_from:
                continue

            dist_to   = len(path_to)   - 1
            dist_from = len(path_from) - 1

            for speed in [SPEED_NORMAL, SPEED_SLOW, SPEED_FAST]:
                ht_to   = travel_half_hours(dist_to,   speed)
                ht_from = travel_half_hours(dist_from, speed)
                total_ht = ht_to + 1 + ht_from  # +1 bányászás

                if sim_t + total_ht > total_half_hours:
                    continue

                # Akkumulátor szimuláció
                b = sim_battery
                t = sim_t
                ok = True

                for i in range(ht_to):
                    b = min(MAX_BATTERY, b + net_move(speed, t))
                    if b < 0:
                        ok = False; break
                    t += 1
                if not ok:
                    continue

                b = min(MAX_BATTERY, b + net_mine(t))
                if b < 0:
                    continue
                t += 1

                for i in range(ht_from):
                    b2 = min(MAX_BATTERY, b + net_move(speed, t + i))
                    if b2 < 0:
                        ok = False; break
                if not ok:
                    continue

                # Pontszám: távolság (közelebb = jobb)
                score = dist_to
                if score < best_score:
                    best_score = score
                    best = mineral
                    best_info = (path_to, path_from, speed)
                break  # Ha egy sebesség működik, elég

        if best is None:
            break  # Nem érhető el több ásvány

        path_to, path_from, speed = best_info
        dist_to = len(path_to) - 1
        ht_to   = travel_half_hours(dist_to, speed)

        route.append(('mineral', best, path_to, speed))
        sim_grid[best[0]][best[1]] = '.'
        remaining.discard(best)

        # Szimulált állapot frissítése
        for i in range(ht_to):
            sim_battery = max(0, min(MAX_BATTERY, sim_battery + net_move(speed, sim_t)))
            sim_t += 1
        sim_battery = max(0, min(MAX_BATTERY, sim_battery + net_mine(sim_t)))
        sim_t += 1
        sim_pos = best

    # Visszatérés az indulóponthoz
    if sim_pos != start:
        path_home = astar(grid, sim_pos, start, rows, cols)
        if path_home and len(path_home) > 1:
            dist_home = len(path_home) - 1
            chosen_speed = SPEED_NORMAL
            for sp in [SPEED_FAST, SPEED_NORMAL, SPEED_SLOW]:
                if sim_t + travel_half_hours(dist_home, sp) <= total_half_hours:
                    chosen_speed = sp
                    break
            route.append(('home', start, path_home, chosen_speed))

    return route


# ===========================================================
# Tkinter alkalmazás
# ===========================================================

class MarsApp:
    def __init__(self, root, grid, start, total_hours):
        self.root = root
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.start = start
        self.total_hours = total_hours
        self.total_half_hours = total_hours * 2
        self.SEC_PER_SIM_HOUR = 10.0   # 1 szim-óra = 10 valódi mp

        # Rover állapot
        self.pos      = start
        self.battery  = MAX_BATTERY
        self.t        = 0   # félórák számlálója
        self.minerals = 0

        self._build_ui()
        self._draw_map()
        self._draw_rover()
        self._update_ui()

        threading.Thread(target=self._run, daemon=True).start()

    # ----------------------------------------------------------
    # UI felépítése
    # ----------------------------------------------------------
    def _build_ui(self):
        self.root.title("🚀 Mars Rover Szimuláció")
        self.root.configure(bg='#0a0a15')
        self.root.resizable(False, False)

        cw = self.cols * CELL
        ch = self.rows * CELL

        main = tk.Frame(self.root, bg='#0a0a15')
        main.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # Térkép canvas
        self.canvas = tk.Canvas(main, width=cw, height=ch,
                                bg='#1a0c06', highlightthickness=1,
                                highlightbackground='#554433')
        self.canvas.pack(side=tk.LEFT, padx=(0, 8))

        # Oldalsáv
        side = tk.Frame(main, bg='#0a0a15', width=INFO_W)
        side.pack(side=tk.LEFT, fill=tk.Y)
        side.pack_propagate(False)

        def label(text, fg='#00ffaa', size=10, bold=False, pady=2):
            font = ('Courier', size, 'bold') if bold else ('Courier', size)
            tk.Label(side, text=text, fg=fg, bg='#0a0a15', font=font).pack(pady=pady)

        def sep():
            label('─' * 26, fg='#223322', size=8)

        label('MARS ROVER', fg='#ff4433', size=14, bold=True, pady=8)
        sep()

        self.tv = {}
        fields = [
            ('daynight',  '☀️  Nappal'),
            ('time',      'Idő:  00:00'),
            ('battery_t', 'Akku: 100.0 %'),
            ('minerals',  'Ásványok:  0 db'),
            ('speed',     'Sebesség:  –'),
            ('status',    'Inicializálás...'),
        ]
        for key, default in fields:
            v = tk.StringVar(value=default)
            self.tv[key] = v
            tk.Label(side, textvariable=v, fg='#00ffaa', bg='#0a0a15',
                     font=('Courier', 10), wraplength=INFO_W-10,
                     justify=tk.LEFT).pack(anchor='w', padx=8, pady=2)

        sep()
        tk.Label(side, text='Akkumulátor:', fg='#888888',
                 bg='#0a0a15', font=('Courier', 9)).pack(anchor='w', padx=8)

        self.bat_cv = tk.Canvas(side, width=INFO_W-16, height=14,
                                bg='#111122', highlightthickness=1,
                                highlightbackground='#334433')
        self.bat_cv.pack(padx=8, pady=4)
        self.bat_bar = self.bat_cv.create_rectangle(0, 0, INFO_W-16, 14,
                                                     fill='#00ee44', outline='')

        sep()
        tk.Label(side, text='Log:', fg='#888888',
                 bg='#0a0a15', font=('Courier', 9)).pack(anchor='w', padx=8)

        self.log_box = tk.Text(side, width=26, height=16,
                               bg='#05050f', fg='#44ffaa',
                               font=('Courier', 8), state=tk.DISABLED,
                               wrap=tk.WORD, highlightthickness=0,
                               relief=tk.FLAT, insertbackground='#00ff44')
        self.log_box.pack(padx=8, pady=4, fill=tk.BOTH, expand=True)

        # Jelmagyarázat
        sep()
        legend_frame = tk.Frame(side, bg='#0a0a15')
        legend_frame.pack(anchor='w', padx=8, pady=2)
        tk.Label(legend_frame, text='Jelmagyarázat:', fg='#888888',
                 bg='#0a0a15', font=('Courier', 8)).grid(row=0, column=0,
                 columnspan=4, sticky='w')
        items = [
            ('.', 'Felszín'), ('#', 'Akadály'),
            ('B', 'Kék jsv.'), ('Y', 'Sárga jsv.'),
            ('G', 'Zöld jsv.'), ('S', 'Start'),
        ]
        for i, (sym, name) in enumerate(items):
            color = COLORS.get(sym, '#888888')
            r, c = divmod(i, 3)
            tk.Label(legend_frame, text='■', fg=color, bg='#0a0a15',
                     font=('Courier', 9)).grid(row=r+1, column=c*2, sticky='w')
            tk.Label(legend_frame, text=name, fg='#aaaaaa', bg='#0a0a15',
                     font=('Courier', 8)).grid(row=r+1, column=c*2+1, sticky='w', padx=(0,6))

    # ----------------------------------------------------------
    # Térkép rajzolása
    # ----------------------------------------------------------
    def _draw_map(self):
        self.cell_ids = {}
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                color = COLORS.get(cell, COLORS['.'])
                x1, y1 = c*CELL, r*CELL
                rid = self.canvas.create_rectangle(
                    x1, y1, x1+CELL, y1+CELL,
                    fill=color, outline='#1a0a04', width=0.4)
                self.cell_ids[(r, c)] = rid

    def _set_cell_color(self, r, c, cell_type):
        color = COLORS.get(cell_type, COLORS['.'])
        self.canvas.itemconfig(self.cell_ids[(r, c)], fill=color)

    # ----------------------------------------------------------
    # Rover rajzolása
    # ----------------------------------------------------------
    def _draw_rover(self):
        if hasattr(self, '_rover_items'):
            for item in self._rover_items:
                self.canvas.delete(item)
        r, c = self.pos
        x = c*CELL + CELL//2
        y = r*CELL + CELL//2
        outer = self.canvas.create_oval(x-5, y-5, x+5, y+5,
                                         fill='#ff2222', outline='white', width=1.5)
        inner = self.canvas.create_oval(x-2, y-2, x+2, y+2,
                                         fill='white', outline='')
        self._rover_items = [outer, inner]

    # ----------------------------------------------------------
    # UI frissítése
    # ----------------------------------------------------------
    def _update_ui(self):
        t = self.t
        h, m = t // 2, (t % 2) * 30
        day = is_day(t)

        self.tv['daynight'].set('☀️  Nappal' if day else '🌙  Éjszaka')
        self.tv['time'].set(f'Idő:  {h:02d}:{m:02d}  /  {self.total_hours}:00')
        self.tv['battery_t'].set(f'Akku: {self.battery:.1f} %')
        self.tv['minerals'].set(f'Ásványok:  {self.minerals} db')

        bw = max(0, int((INFO_W-16) * self.battery / MAX_BATTERY))
        bc = ('#00ee44' if self.battery > 30
              else '#ffaa00' if self.battery > 15
              else '#ff3300')
        self.bat_cv.coords(self.bat_bar, 0, 0, bw, 14)
        self.bat_cv.itemconfig(self.bat_bar, fill=bc)

        self._draw_rover()

    # ----------------------------------------------------------
    # Napló
    # ----------------------------------------------------------
    def _log(self, msg):
        def _do():
            h, m = self.t // 2, (self.t % 2) * 30
            self.log_box.config(state=tk.NORMAL)
            self.log_box.insert(tk.END, f'[{h:02d}:{m:02d}] {msg}\n')
            self.log_box.see(tk.END)
            self.log_box.config(state=tk.DISABLED)
        self.root.after(0, _do)

    # ----------------------------------------------------------
    # Mozgás animáció
    # ----------------------------------------------------------
    def _travel(self, path, speed):
        """Végrehajt egy mozgást a megadott útvonalon és sebességgel."""
        if len(path) <= 1:
            return

        dist = len(path) - 1
        ht   = travel_half_hours(dist, speed)
        sec_per_block = (self.SEC_PER_SIM_HOUR / 2) / speed

        for step in range(ht):
            # 'speed' blokk mozgás ebben a félórában
            for b in range(speed):
                idx = step * speed + b + 1
                if idx >= len(path):
                    break
                self.pos = path[idx]
                self.root.after(0, self._draw_rover)
                time.sleep(sec_per_block)

            # Félóra vége: akkumulátor frissítés
            net = net_move(speed, self.t)
            self.battery = max(0.0, min(MAX_BATTERY, self.battery + net))
            self.t += 1
            self.root.after(0, self._update_ui)

    # ----------------------------------------------------------
    # Bányászás
    # ----------------------------------------------------------
    def _mine(self, pos):
        """Végrehajt egy bányászást az adott pozícióban."""
        sec = self.SEC_PER_SIM_HOUR / 2
        self.root.after(0, self.tv['status'].set, '⛏️  Bányászás...')

        # Villogás-effekt
        r, c = pos
        for _ in range(4):
            self.root.after(0, self._set_cell_color, r, c, '.')
            time.sleep(sec / 8)
            self.root.after(0, lambda r=r, c=c: self.canvas.itemconfig(
                self.cell_ids[(r, c)], fill='#ffffff'))
            time.sleep(sec / 8)

        net = net_mine(self.t)
        self.battery = max(0.0, min(MAX_BATTERY, self.battery + net))
        self.t += 1
        self.minerals += 1

        self.root.after(0, self._set_cell_color, r, c, 'collected')
        self.root.after(0, self._update_ui)

    # ----------------------------------------------------------
    # Fő szimulációs szál
    # ----------------------------------------------------------
    def _run(self):
        self.root.after(0, self.tv['status'].set, '⚙️  Tervezés...')
        self._log('Útvonal tervezése...')

        route = plan_route(self.grid, self.start,
                           self.rows, self.cols, self.total_half_hours)

        n_minerals = sum(1 for s in route if s[0] == 'mineral')
        self._log(f'Terv kész: {n_minerals} ásvány célzott')
        self.root.after(0, self.tv['status'].set, f'🚀 Indulás! ({n_minerals} cél)')
        time.sleep(1.5)

        for step in route:
            kind = step[0]
            speed_names = {1: 'Lassú', 2: 'Normál', 3: 'Gyors'}

            if kind == 'mineral':
                _, pos, path_to, speed = step
                r, c = pos
                mineral_type = self.grid[r][c]
                sname = speed_names[speed]

                self.root.after(0, self.tv['speed'].set,
                                f'Sebesség: {sname} ({speed} bl/fó)')
                self.root.after(0, self.tv['status'].set,
                                f'🚗 → {mineral_type} ({r},{c})')
                self._log(f'Cél: {mineral_type} @({r},{c}) [{sname}]')

                self._travel(path_to, speed)
                self._mine(pos)
                self._log(f'✓ Összegyűjtve! Összesen: {self.minerals}')

            elif kind == 'home':
                _, pos, path_home, speed = step
                sname = speed_names.get(speed, str(speed))
                self.root.after(0, self.tv['speed'].set,
                                f'Sebesség: {sname} ({speed} bl/fó)')
                self.root.after(0, self.tv['status'].set, '🏠 Visszatérés...')
                self._log('Visszatérés az induló álláshoz')
                self._travel(path_home, speed)

        self.root.after(0, self.tv['status'].set, '✅ Misszió teljesítve!')
        self.root.after(0, self.tv['speed'].set, 'Sebesség:  0')
        self._log(f'🎉 Kész! {self.minerals} ásvány begyűjtve')
        self._log(f'Végső akku: {self.battery:.1f}%')


# ===========================================================
# Belépési pont
# ===========================================================

def main():
    # A térképfájl keresése: argumentumként, mellette, vagy alapértelmezett helyen
    if len(sys.argv) > 2:
        map_path = sys.argv[2]
    else:
        candidates = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mars_map_50x50.txt'),
            'mars_map_50x50.txt',
        ]
        map_path = next((p for p in candidates if os.path.exists(p)), candidates[0])

    if len(sys.argv) > 1:
        try:
            hours = int(sys.argv[1])
        except ValueError:
            hours = 24
    else:
        try:
            raw = input('Megadandó időkeret (óra, min 24): ').strip()
            hours = int(raw) if raw else 24
        except (ValueError, EOFError):
            hours = 24

    if hours < 24:
        print('Minimum 24 óra szükséges. 24 órára állítva.')
        hours = 24

    print(f'Időkeret: {hours} óra  |  1 szim-óra = 10 valódi mp')
    print(f'Térkép betöltése: {map_path}')

    grid, start = parse_map(map_path)

    if start is None:
        print("HIBA: 'S' kiindulópont nem található a térképen!")
        sys.exit(1)

    print(f'Start: {start}')

    root = tk.Tk()
    app = MarsApp(root, grid, start, hours)
    root.mainloop()


if __name__ == '__main__':
    main()
