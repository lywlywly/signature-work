import os

DATA_DIR = "data_new/"
assert os.path.exists(DATA_DIR), f"DATA_DIR={DATA_DIR} does not exist."
ROLES_DIR = os.path.join(DATA_DIR, "roles")
os.makedirs(ROLES_DIR, exist_ok=True)
HTML_DIR = os.path.join(DATA_DIR, "html")
os.makedirs(HTML_DIR, exist_ok=True)
CHAMP_ITEMS_DIR = os.path.join(DATA_DIR, "champ_items")
os.makedirs(CHAMP_ITEMS_DIR, exist_ok=True)
CHAMP_ITEM_PICK_WIN_RATE = os.path.join(CHAMP_ITEMS_DIR, "pick_win_rate")
os.makedirs(CHAMP_ITEM_PICK_WIN_RATE, exist_ok=True)
CONVERT_DIR = os.path.join(CHAMP_ITEMS_DIR, "convert")
os.makedirs(CONVERT_DIR, exist_ok=True)
roles = ["top", "jungle", "mid", "adc", "support"]
