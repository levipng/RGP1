import ctypes
import sys
import pygame

fajlnev = "windows_c.dll" if sys.platform.startswith('win') else "linux_c.so"

try:
    ckonyvtar0 = ctypes.CDLL(rf"./{fajlnev}")
except OSError as hibakod:
    print(f"{hibakod}")
    sys.exit(1)

# Beállítjuk a függvény típusait
ckonyvtar0.duplaz.argtypes = [ctypes.c_int]       # bemenet: egy int
ckonyvtar0.duplaz.restype = ctypes.c_int          # visszatérési érték: int

print(ckonyvtar0.duplaz(3))