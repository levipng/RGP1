import ctypes
import os
import sys

# Automatikusan kiválasztjuk a megfelelő kiterjesztést
if sys.platform.startswith('win'):
    fajl_nev = "win_c.dll"
else:
    fajl_nev = "linux_c.so"

# A library fájlnak ugyanabban a mappában kell lennie, mint a python szkriptnek
eleresi_ut = os.path.join(os.path.dirname(__file__), fajl_nev)

# Betöltjük a C library-t
try:
    c_konyvtar = ctypes.CDLL(eleresi_ut)
except OSError as e:
    print(f"Hiba a library betöltésekor: {e}")
    print("Ellenőrizd, hogy a .so / .dll fájl létezik-e ugyanabban a mappában!")
    sys.exit(1)

# Beállítjuk a függvény típusait
c_konyvtar.duplaz.restype = ctypes.c_int          # visszatérési érték: int
c_konyvtar.duplaz.argtypes = [ctypes.c_int]       # bemenet: egy int

# Most már használhatjuk úgy, mint egy sima python függvényt
def c(x):
    return c_konyvtar.duplaz(x)

# Teszt
print(c(3))          # kiírja: 6
print(c(10))         # kiírja: 20
print(c(-7))         # kiírja: -14
