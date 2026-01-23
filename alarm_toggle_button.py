from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class AlarmToggleButton(QPushButton):
    """
    Pure UI component for toggling the alarm state.
    Updated to use Bell emoji (🔔) to distinguish from clock.
    """
    def __init__(self, parent=None):
        super().__init__("🔔", parent)
        self.setCheckable(True)
        self.setFixedSize(32, 32)
        self.setToolTip("Toggle Alarm (ON/OFF)")
        self.setFont(QFont("Segoe UI Emoji", 14))
        self.setCursor(Qt.PointingHandCursor)

        self._update_style(False)
        self.toggled.connect(self._update_style)

    def _update_style(self, checked):
        if checked:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #FFD93D;
                    color: #2C3E50;
                    border: 2px solid #FFD93D;
                    border-radius: 16px;
                }
                QPushButton:hover {
                    background-color: #FFEA85;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    color: white;
                    background-color: transparent;
                    border: 2px solid rgba(255, 255, 255, 0.2);
                    border-radius: 16px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                }
            """)
