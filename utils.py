from PyQt5.QtGui import QColor
from datetime import datetime, timedelta, timezone

# Constants
UTC_TZ = timezone.utc
KST_TZ = timezone(timedelta(hours=9))

# Colors
# Modern Palette
# Day: Warm/Bright (e.g., Soft Orange-Yellow-ish or Bright Blue)
# Night: Dark (Midnight Blue)
# Transition: Neutral/Sunset
COLOR_DAY_BG = "#FFFAEA" # Light warm
COLOR_DAY_TEXT = "#5C4B2E"

COLOR_NIGHT_BG = "#1A1A2E" # Deep Blue
COLOR_NIGHT_TEXT = "#E6E6E6"

COLOR_TRANSITION_BG = "#F4E1D2" # Sunset-ish
COLOR_TRANSITION_TEXT = "#4A3B2A"

COLOR_ACCENT = "#FF6B6B" # For selection or highlights
COLOR_CURRENT_TIME = "#4ECDC4" # To mark 'now'
COLOR_TIMELINE_BG = "#eeeeee" # Light gray for timeline area

def get_color_for_hour(hour_24):
    """
    Returns (bg_color, text_color) based on the hour.
    Day: 08:00 - 17:00 (17 is 5 PM)
    Night: 22:00 (10 PM) - 05:00
    Transition: Rest
    """
    # Check ranges
    # Day: 8 <= h < 18 (Ends at 17:59, so 17 is included? "Until 5pm" usually implies 17 is the last hour or 16?)
    # Request: "08 ~ 17 is Day" -> 8,9...17.
    # "22 ~ 05 is Night" -> 22,23,0,1,2,3,4,5.
    
    if 8 <= hour_24 <= 17:
        return COLOR_DAY_BG, COLOR_DAY_TEXT
    elif (22 <= hour_24 <= 23) or (0 <= hour_24 <= 5):
        return COLOR_NIGHT_BG, COLOR_NIGHT_TEXT
    else:
        return COLOR_TRANSITION_BG, COLOR_TRANSITION_TEXT

def get_current_time_utc():
    return datetime.now(UTC_TZ)

def get_current_time_kst():
    return datetime.now(KST_TZ)

def format_am_pm(hour_24):
    """Returns 'am' or 'pm' and the 12-hour format hour."""
    am_pm = "am" if hour_24 < 12 else "pm"
    h_12 = hour_24 % 12
    if h_12 == 0:
        h_12 = 12
    return str(h_12), am_pm
