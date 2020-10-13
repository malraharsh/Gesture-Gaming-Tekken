import ctypes
import time

SendInput = ctypes.windll.user32.SendInput


W = 0x11
A = 0x1E
S = 0x1F
D = 0x20

#http://www.philipstorr.id.au/pcbook/book3/scancode.htm
# http://www.scs.stanford.edu/10wi-cs140/pintos/specs/kbd/scancodes-1.html
U = 0x16
I = 0x17
O = 0x18
J = 0x24
K = 0x25
L = 0x26


Up=0x48
Left= 0x4B
Right= 0x4D
Down= 0x50
# And the scan codes for the arrow keys are:

# Up: 0x48
# Left: 0x4B
# Right: 0x4D
# Down: 0x50




# C struct redefinitions 
PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time",ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                 ("mi", MouseInput),
                 ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

# Actuals Functions

def PressKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


key2hex = {'T': 84,
 'Y': 89,
 'U': 85,
 'I': 73,
 'O': 79,
 'P': 80,
 'G': 71,
 'H': 72,
 'J': 74,
 'K': 75,
 'L': 76,
 ';': 59,
 'V': 86,
 'B': 66,
 'N': 78,
 'M': 77,
 ',': 44,
 '.': 46,
 '\r': 13,
 'Q': 81,
 'W': 87,
 'E': 69,
 'R': 82,
 'A': 65,
 'S': 83,
 'D': 68,
 'F': 70,
 'Z': 90,
 'X': 88,
 'C': 67,
 '2': 50,
 '3': 51}

if __name__ == '__main__':
    PressKey(0x11)
    time.sleep(1)
    ReleaseKey(0x11)
    time.sleep(1)


