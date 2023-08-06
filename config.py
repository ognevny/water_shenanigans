FPS = 30

COLORS: dict[str : tuple[int, int, int]] = {
    "white" : (255, 255, 255), 
    "black" : (0, 0, 0),
    "sky" : (0xAA, 0xA1, 0xC8)
}

W = 64
H = 64

RANDOM_CRITS = True

GLOBAL_X_OFFSET = 292
GLOBAL_Y_OFFSET = 100

FONT_SIZE = 48

MAP_LEN = 9

TEXT_MAP = [
    [3, 3, 3, 3, 3, 3, 3, 3, 3],
    [3, 3, 3, 3, 3, 3, 3, 3, 1],
    [1, 1, 3, 3, 3, 3, 3, 1, 1],
    [1, 1, 1, 3, 3, 3, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1],
    [2, 2, 2, 1, 2, 1, 1, 2, 2],
    [2, 2, 2, 2, 2, 2, 1, 2, 2],
    [2, 2, 2, 2, 2, 2, 2, 2, 2],
    [2, 2, 2, 2, 2, 2, 2, 2, 2]

]

USE_MAP_LEN = False
DEBUG = False
RECT_OFFSET_X = 5; RECT_OFFSET_Y = 40

CANTEEN_FRAME_DURATION = 0.15 / FPS * 38