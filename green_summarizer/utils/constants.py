import os

# Default Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'history.db')

# Colors
COLOR_PRIMARY_GREEN = "#2E7D32"
COLOR_LIGHT_GREEN = "#E8F5E9"
COLOR_DARK_TEXT = "#1B1B1B"
COLOR_MUTED_TEXT = "#666666"

# Battery / Power Defaults
DEFAULT_BATTERY_CAPACITY_MAH = 4000
DEFAULT_NOMINAL_VOLTAGE = 3.85
DEFAULT_GRID_FACTOR_GCO2E_PER_KWH = 708.2 # Default for India
