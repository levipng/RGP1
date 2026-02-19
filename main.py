import ctypes
import sys

win=False
if sys.platform.startswith('win'):
    fajl_nev = "windows_c.dll"
    win=True
else:
    fajl_nev = "linux_c.so"
    win=False

try:
    if win:
        c_konyvtar = ctypes.CDLL(rf".\{fajl_nev}")
    else:
        c_konyvtar = ctypes.CDLL(rf"./{fajl_nev}")
except OSError as hibakod:
    print(f"{hibakod}")
    sys.exit(1)

# Beállítjuk a függvény típusait
c_konyvtar.duplaz.argtypes = [ctypes.c_int]       # bemenet: egy int
c_konyvtar.duplaz.restype = ctypes.c_int          # visszatérési érték: int

print(c_konyvtar.duplaz(3))
