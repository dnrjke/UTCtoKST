from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, 
                             QHBoxLayout, QScrollArea, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor

import utils

class TimeSlotWidget(QFrame):
    """
    Displays a single hour block (e.g., "3 pm").
    """
    def __init__(self, dt_obj, is_top=True):
        super().__init__()
        self.dt = dt_obj
        self.is_top = is_top # True for UTC (Top), False for KST (Bottom)
        self.setFixedSize(60, 100) # Width, Height (Increased to 100 for safety)
        
        # Colors
        self.bg_color, self.text_color = utils.get_color_for_hour(self.dt.hour)
        
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setup_ui()
        self.update_style()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5) # Top/Bottom padding
        layout.setSpacing(0)
        
        # Hour Number
        h_12, am_pm = utils.format_am_pm(self.dt.hour)
        
        self.lbl_hour = QLabel(h_12)
        self.lbl_hour.setAlignment(Qt.AlignCenter)
        font_h = QFont("Segoe UI", 16, QFont.Bold)
        self.lbl_hour.setFont(font_h)
        
        # AM/PM
        self.lbl_ampm = QLabel(am_pm)
        self.lbl_ampm.setAlignment(Qt.AlignTop | Qt.AlignHCenter) 
        font_ap = QFont("Segoe UI", 9) 
        self.lbl_ampm.setFont(font_ap)
        # Increased height to prevent clipping of descenders (p, g, y)
        self.lbl_ampm.setFixedHeight(25) 

        layout.addWidget(self.lbl_hour)
        layout.addWidget(self.lbl_ampm)
        layout.addStretch() 

    def update_style(self, selected=False):
        border_val = '3px solid #FF6B6B' if selected else '3px solid transparent'
        
        style = f"""
            QFrame {{
                background-color: {self.bg_color};
                border-radius: 8px;
                border: {border_val};
            }}
            QLabel {{
                color: {self.text_color};
                background: transparent;
                border: none;
            }}
        """
        self.setStyleSheet(style)


from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class TimeColumnWidget(QWidget):
    """
    Vertical container: UTC Slot (Top) + KST Slot (Bottom)
    """
    clicked = pyqtSignal(int) # Emits index when clicked

    def __init__(self, index, utc_dt, kst_dt):
        super().__init__()
        self.index = index
        self.utc_dt = utc_dt
        self.kst_dt = kst_dt
        self.is_selected = False
        
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4) 
        layout.setSpacing(8) # Reverted to 8 as per original design
        
        self.utc_slot = TimeSlotWidget(self.utc_dt, is_top=True)
        self.kst_slot = TimeSlotWidget(self.kst_dt, is_top=False)
        
        layout.addWidget(self.utc_slot)
        layout.addWidget(self.kst_slot)
        
        # Make clickable
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        self.clicked.emit(self.index)
        super().mousePressEvent(event)

    def set_selected(self, selected):
        self.is_selected = selected
        self.utc_slot.update_style(selected)
        self.kst_slot.update_style(selected)


class TimelineContainer(QWidget):
    """
    Horizontal scrollable container for the 24 columns.
    """
    slot_selected = pyqtSignal(object, object) # Emits (utc_dt, kst_dt)

    def __init__(self):
        super().__init__()
        self.columns = []
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 15) # 15 bottom to balance
        self.main_layout.setSpacing(5) # Spacing between columns
        self.main_layout.setAlignment(Qt.AlignLeft)
        
        # Ensure transparent background
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"background-color: {utils.COLOR_TIMELINE_BG};")

    def populate(self, start_utc_dt):
        """
        Populate with 24 hours starting from start_utc_dt.
        start_utc_dt: datetime object (UTC) for the first slot.
        """
        # Clear existing
        for i in reversed(range(self.main_layout.count())): 
            widget = self.main_layout.itemAt(i).widget()
            if widget: widget.deleteLater()
        self.columns = []

        curr_utc = start_utc_dt
        for i in range(24):
            # Calculate corresponding KST
            curr_kst = curr_utc.astimezone(utils.KST_TZ)
            
            col = TimeColumnWidget(i, curr_utc, curr_kst)
            col.clicked.connect(self.handle_column_click)
            self.main_layout.addWidget(col)
            self.columns.append(col)
            
            curr_utc += utils.timedelta(hours=1)

    def handle_column_click(self, index):
        for col in self.columns:
            col.set_selected(False)
        
        tgt = self.columns[index]
        tgt.set_selected(True)
        
        self.slot_selected.emit(tgt.utc_dt, tgt.kst_dt)

    def select_index(self, index):
        if 0 <= index < len(self.columns):
            self.handle_column_click(index)
