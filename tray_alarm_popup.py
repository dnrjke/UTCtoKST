from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication, QFont

class TrayAlarmPopup(QWidget):
    """
    Custom QWidget-based popup.
    Displayed at the bottom-right tray area.
    """
    def __init__(self, message):
        super().__init__(
            flags=Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )

        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowOpacity(0.98)
        self.setAttribute(Qt.WA_TranslucentBackground) # For rounded corners support

        self.setup_ui(message)
        self._move_to_tray_area()

    def setup_ui(self, message):
        self.container = QFrame(self)
        self.container.setStyleSheet("""
            QFrame {
                background-color: #2C3E50;
                border: 2px solid #FF6B6B;
                border-radius: 12px;
            }
            QLabel {
                color: white;
                background: transparent;
                border: none;
            }
        """)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(20, 15, 20, 15)

        self.lbl_title = QLabel("ALARM")
        self.lbl_title.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.lbl_title.setStyleSheet("color: #FF6B6B;")
        
        self.lbl_message = QLabel(message)
        self.lbl_message.setFont(QFont("Segoe UI", 12))
        self.lbl_message.setWordWrap(True)
        self.lbl_message.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.lbl_title, 0, Qt.AlignLeft)
        layout.addWidget(self.lbl_message)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.container)

        self.setFixedSize(280, 110) # Slightly larger for longer custom messages

    def _move_to_tray_area(self):
        screen = QGuiApplication.primaryScreen()
        geo = screen.availableGeometry()

        x = geo.right() - self.width() - 10
        y = geo.bottom() - self.height() - 10
        self.move(x, y)

    def mousePressEvent(self, event):
        self.close()
