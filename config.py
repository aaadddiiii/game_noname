# --- WINDOW LAYOUT ---
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 740

MAP_WIDTH = 800
MAP_HEIGHT = 540
CELL_SIZE = 32

LOG_PANEL_X = 800
LOG_PANEL_WIDTH = 400
LOG_PANEL_HEIGHT = 740

OPT_PANEL_Y = 540
OPT_PANEL_WIDTH = 800
OPT_PANEL_HEIGHT = 200

# --- COLORS ---
BG_MAIN = (10, 10, 10)
BG_LOGS = (20, 20, 25)
BG_OPTS = (15, 20, 20)

C_WHITE = (220, 220, 220)
C_RED = (255, 80, 80)
C_GREEN = (80, 255, 80)
C_BLUE = (100, 150, 255)
C_YELLOW = (255, 215, 0)
C_ORANGE = (255, 165, 0)

# --- TEXT FORMATTING ---
TEXT_STYLES = {
    "**": {"color": C_RED, "bold": False},
    "*": {"color": C_RED, "bold": True},
    "++": {"color": C_BLUE, "bold": True},
    "--": {"color": C_YELLOW, "bold": False},
    "##": {"color": C_ORANGE, "bold": True},
    "_": {"color": C_WHITE, "bold": True},
}
