from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QWidget, QFrame)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont, QColor
from alarm_controller import DEFAULT_ALARM_MESSAGE, DEFAULT_PRESETS

class AlarmSettingsDialog(QDialog):
    """
    Modal dialog for configuring alarm messages with 3 presets and full sync.
    Restored yellow highlight styling for active presets and refined frameless UI.
    """
    def __init__(self, alarm_controller, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.alarm_controller = alarm_controller
        self._current_index = self.alarm_controller.active_preset_index
        self.setFixedWidth(420)
        
        # Stylesheet (Consolidated with yellow active highlights)
        self.setStyleSheet("""
            QWidget#mainContainer {
                background-color: #2C3E50;
                border-radius: 12px;
            }
            QLabel {
                color: #ECF0F1;
                font-family: 'Segoe UI';
                background: transparent;
            }
            QLineEdit {
                background-color: #34495E;
                color: white;
                border: 1px solid #4CA1AF;
                border-radius: 6px;
                padding: 12px;
                font-size: 18px;
            }
            QPushButton {
                color: white;
                border: 1px solid transparent;
                border-radius: 6px;
                padding: 12px 20px;
                font-family: 'Segoe UI';
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover { background-color: #5bb2bf; }
            
            /* YELLOW ACTIVE HIGHLIGHT */
            QPushButton:checked {
                background-color: #FFD93D;
                color: #2C3E50;
                border: 1px solid #FFD93D;
            }
            
            QPushButton#applyBtn { background-color: #4CA1AF; }
            QPushButton#resetBtn {
                background-color: #5D6D7E;
                border: 1px solid rgba(174, 182, 191, 0.5);
                color: #D5D8DC;
            }
            QPushButton#resetBtn:hover { background-color: #707B7C; color: white; }
            
            QPushButton#presetBtn {
                background-color: #34495E;
                border: 1px solid #4CA1AF;
                padding: 0px;
                font-size: 20px; /* Highly visible numbers */
            }
            QPushButton#presetBtn:hover { background-color: #4CA1AF; }
            /* Specific fix for Preset checked state */
            QPushButton#presetBtn:checked {
                background-color: #FFD93D;
                color: #2C3E50;
                border: 1px solid #FFD93D;
            }
            
            QPushButton#closeBtn {
                background: transparent;
                color: #ECF0F1;
                font-size: 20px;
                border: none;
                padding: 0px;
            }
            QPushButton#closeBtn:hover { color: #FF6B6B; }
        """)
        
        self.setup_ui()
        self.load_state()
        
        self._old_pos = None

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.container = QFrame()
        self.container.setObjectName("mainContainer")
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 25)
        self.container_layout.setSpacing(20)
        
        # Header
        self.title_bar = QWidget()
        self.title_bar.setFixedHeight(45)
        self.title_bar.setStyleSheet("background-color: #1A252F; border-top-left-radius: 10px; border-top-right-radius: 10px;")
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(15, 0, 10, 0)
        
        lbl_title = QLabel("Alarm Settings")
        lbl_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        
        btn_close = QPushButton("✕")
        btn_close.setObjectName("closeBtn")
        btn_close.setFixedSize(30, 30)
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.clicked.connect(self.reject)
        
        title_layout.addWidget(lbl_title)
        title_layout.addStretch()
        title_layout.addWidget(btn_close)
        self.container_layout.addWidget(self.title_bar)
        
        # Content
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(25, 0, 25, 0)
        content_layout.setSpacing(18)
        
        top_row = QHBoxLayout()
        lbl_msg = QLabel("Alarm message:")
        lbl_msg.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFD93D;")
        top_row.addWidget(lbl_msg)

        self.preset_buttons = []
        for i in range(3):
            btn = QPushButton(str(i+1))
            btn.setObjectName("presetBtn")
            btn.setCheckable(True)
            btn.setFixedSize(45, 45) # Slightly larger
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(self._create_preset_handler(i))
            self.preset_buttons.append(btn)
            top_row.addWidget(btn)
            
        top_row.addStretch()
        content_layout.addLayout(top_row)

        self.txt_message = QLineEdit()
        self.txt_message.setPlaceholderText("Enter notification message...")
        content_layout.addWidget(self.txt_message)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        
        # "Reset Current" as requested
        self.btn_reset = QPushButton("Reset current")
        self.btn_reset.setObjectName("resetBtn")
        self.btn_reset.setCursor(Qt.PointingHandCursor)
        self.btn_reset.setFixedHeight(45)
        self.btn_reset.clicked.connect(self.reset_preset)
        
        self.btn_apply = QPushButton("Apply")
        self.btn_apply.setObjectName("applyBtn")
        self.btn_apply.setCursor(Qt.PointingHandCursor)
        self.btn_apply.setFixedHeight(45)
        self.btn_apply.setDefault(True)
        self.btn_apply.clicked.connect(self.apply_changes)
        
        btn_layout.addWidget(self.btn_reset)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_apply)
        
        content_layout.addLayout(btn_layout)
        self.container_layout.addLayout(content_layout)
        self.main_layout.addWidget(self.container)

    def load_state(self):
        """Init UI with current controller state."""
        idx = self.alarm_controller.active_preset_index
        message = self.alarm_controller.message
        self.txt_message.setText(message)
        self._update_preset_selection_ui(idx)

    def _update_preset_selection_ui(self, index):
        """Update toggle state of buttons."""
        for i, btn in enumerate(self.preset_buttons):
            btn.setChecked(i == index)
        self._current_index = index

    def _create_preset_handler(self, idx):
        def handler():
            # Load stored preset message into textbox when clicked
            msg = self.alarm_controller.get_preset_message(idx)
            self.txt_message.setText(msg)
            self._update_preset_selection_ui(idx)
        return handler

    def apply_changes(self):
        """Commits current dialog state to controller."""
        msg = self.txt_message.text()
        self.alarm_controller.set_active_preset(self._current_index, msg)
        self.accept()

    def reset_preset(self):
        """Resets the currently selected preset to default."""
        new_msg = self.alarm_controller.reset_preset(self._current_index)
        self.txt_message.setText(new_msg)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self._old_pos is not None:
            delta = QPoint(event.globalPos() - self._old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self._old_pos = None
