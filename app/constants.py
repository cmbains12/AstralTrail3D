import numpy as np

CONFIG_PATH = "config.json"
CONFIG_DEFAULTS = {
    "window": {
        "width": 800,
        "height": 600,
        "title": "Astral Trail",
        "fps": 90
    },
    "camera": {
        "position": np.array([1.0, 2.0, -5.0], dtype=np.float32),
        "orientation": np.array([
            np.array([1.0, 0.0, 0.0], dtype=np.float32),
            np.array([0.0, 1.0, 0.0], dtype=np.float32),
            np.array([0.0, 0.0, 1.0], dtype=np.float32)
        ], dtype=np.float32),
        "fov": 60.0,
        "near_plane": 0.1,
        "far_plane": 500.0
    }
}

COLOURS = {
    "black": (0, 0, 0, 255),
    "white": (255, 255, 255, 255),
    "red": (255, 0, 0, 255),
    "green": (0, 255, 0, 255),
    "blue": (0, 0, 255, 255),
    "yellow": (255, 255, 0, 255),
    "cyan": (0, 255, 255, 255),
    "magenta": (255, 0, 255, 255),
    "darkGray": (169, 169, 169, 255),
    "gray": (128, 128, 128, 255),
    "lightGray": (211, 211, 211, 255),
    "darkRed": (139, 0, 0, 255),
    "darkGreen": (0, 100, 0, 255),
    "darkBlue": (0, 0, 139, 255),
    "orange": (255, 165, 0, 255),
    "purple": (128, 0, 128, 255),
    "pink": (255, 192, 203, 255),
    "brown": (165, 42, 42, 255),
    "gold": (255, 215, 0, 255),
}

COS30 = np.cos(np.radians(30))
PI = np.pi
COS45 = np.cos(np.radians(45))

KEYS_INITIAL_STATE = {
    'key_w': False,
    'key_a': False,
    'key_s': False,
    'key_d': False,
    'key_esc': False,
    'key_space': False,
    'key_lshift': False,
    'key_lctrl': False,
    'key_lalt': False,
    'key_q': False,
    'key_e': False,
    'key_space': False,
    'key_z': False,
    'key_c': False,
    'key_x': False,
    'key_r': False,
    'key_f': False,
    'key_v': False,
    'key_t': False,
    'key_g': False,
    'key_b': False,
    'key_y': False,
    'key_h': False,
    'key_n': False,
    'key_u': False,
    'key_j': False,
    'key_m': False,
    'key_i': False,
    'key_k': False,
    'key_o': False,
    'key_l': False,
    'key_p': False,
    'key_one': False,
    'key_two': False,
    'key_three': False,
    'key_four': False,
    'key_five': False,
    'key_six': False,
    'key_seven': False,
    'key_eight': False,
    'key_nine': False,
    'key_zero': False,
    'key_minus': False,
    'key_plus': False,
    'key_backspace': False,
    'key_enter': False,
    'key_tab': False,
    'key_rshift': False,
    'key_rctrl': False,
    'key_ralt': False,
}