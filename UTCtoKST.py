import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QSystemTrayIcon, QMenu, 
                             QAction, QVBoxLayout, QWidget, QScrollArea, QLabel, 
                             QHBoxLayout, QPushButton)
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QIcon, QFont, QCursor
from PyQt5.QtNetwork import QLocalServer, QLocalSocket

import utils
from ui_components import TimelineContainer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UTC <-> KST Converter")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground) # Enable transparent window for rounded corners
        self.resize(800, 340) # Compact height to fit content exactly
        
        # Stylesheet for Window
        self.setStyleSheet("""
            QMainWindow {
                background-color: transparent;
                border: none;
            }
            QLabel {
                color: white;
                font-family: 'Segoe UI';
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QWidget#centralWidget {
                 background-color: #2C3E50;
                 border-radius: 10px;
            }
        """)
        
        self.init_ui()
        self.init_timer()

    def init_ui(self):
        self.central_widget = QWidget()
        self.central_widget.setObjectName("centralWidget")
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0) # Remove default spacing for precise control
        
        # --- Top Bar ---
        self.top_bar = QWidget()
        self.top_bar.setStyleSheet("background-color: rgba(0,0,0,0.2); border-top-left-radius: 10px; border-top-right-radius: 10px;")
        self.top_hbox = QHBoxLayout(self.top_bar)
        
        # Date/Time Display
        self.lbl_datetime = QLabel("Date Time")
        self.lbl_datetime.setFont(QFont("Segoe UI", 10))
        
        # Spacer
        self.top_hbox.addWidget(self.lbl_datetime)
        self.top_hbox.addStretch()
        
        # Close Button (App Hide)
        self.btn_close = QPushButton("X")
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.setStyleSheet("""
            QPushButton {
                color: white; 
                background: transparent; 
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                color: #FF6B6B;
            }
        """)
        self.btn_close.clicked.connect(self.hide) # Just hide, don't exit
        self.top_hbox.addWidget(self.btn_close)
        
        self.layout.addWidget(self.top_bar)
        
        # --- Info Bar (Selection Info) ---
        self.info_label = QLabel("Select a time slot to see details.")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setFont(QFont("Segoe UI", 12))
        self.info_label.setStyleSheet("color: #FFD93D; background-color: #2C3E50; padding: 5px;")
        self.layout.addWidget(self.info_label)

        # --- Timeline Area ---
        class HorizontalScrollArea(QScrollArea):
             def wheelEvent(self, event):
                 if event.angleDelta().y() != 0:
                     # Scroll horizontally instead of vertically
                     self.horizontalScrollBar().setValue(
                         self.horizontalScrollBar().value() - event.angleDelta().y()
                     )
                     event.accept()
                 else:
                     super().wheelEvent(event)

        self.scroll_area = HorizontalScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Custom Scrollbar Style (Thin & Modern)
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background: transparent;
                background-color: transparent;
            }}
            QScrollBar:horizontal {{
                border: none;
                background: {utils.COLOR_TIMELINE_BG};
                height: 8px; /* Thin */
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:horizontal {{
                background: #4CA1AF;
                min-width: 20px;
                border-radius: 4px;
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
                background: none;
            }}
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background: none;
            }}
        """)
        
        self.timeline = TimelineContainer()
        self.timeline.slot_selected.connect(self.update_info_label)
        
        self.scroll_area.setWidget(self.timeline)
        self.layout.addWidget(self.scroll_area)
        
        # --- Populate Data ---
        self.refresh_timeline()

    def init_timer(self):
        # Update top bar time every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_top_bar)
        self.timer.start(1000)
        self.update_top_bar()

    def update_top_bar(self):
        now_utc = utils.get_current_time_utc()
        now_kst = utils.get_current_time_kst()
        
        txt = f"UTC: {now_utc.strftime('%Y-%m-%d %H:%M:%S')}  |  KST: {now_kst.strftime('%Y-%m-%d %H:%M:%S')}"
        self.lbl_datetime.setText(txt)

    def refresh_timeline(self):
        # Start from current UTC hour rounded down
        now_utc = utils.get_current_time_utc().replace(minute=0, second=0, microsecond=0)
        
        # "UTC current time aligned to left" -> Start at now_utc
        self.timeline.populate(now_utc)
        
        # Select the first one by default (Current time)
        self.timeline.select_index(0)

    def update_info_label(self, utc_dt, kst_dt):
        now_utc = utils.get_current_time_utc().replace(tzinfo=utils.UTC_TZ)
        utc_dt = utc_dt.replace(tzinfo=utils.UTC_TZ)
        
        # Diff from NOW
        diff = utc_dt - now_utc
        total_seconds = diff.total_seconds()
        
        # Color coding for relative time
        if abs(total_seconds) < 60:
            diff_str = "<span style='color: #FF6B6B;'>Right Now</span>"
        else:
            is_future = total_seconds > 0
            secs = abs(int(total_seconds))
            hours = secs // 3600
            minutes = (secs % 3600) // 60
            
            time_parts = []
            if hours > 0:
                time_parts.append(f"{hours} hours")
            if minutes > 0:
                time_parts.append(f"{minutes} min")
                
            time_txt = " ".join(time_parts) if time_parts else "0 min"
            
            if is_future:
                # Future: Teal/Modern
                diff_str = f"<span style='color: #4ECDC4;'>in {time_txt}</span>"
            else:
                # Past: Subtle Gray
                diff_str = f"<span style='color: #95A5A6;'>{time_txt} ago</span>"
            
        # Standardize main text to white, highlight times in yellow
        txt = (f"Selected: <span style='color: #FFD93D;'>UTC {utc_dt.strftime('%H:%M')}</span> | "
               f"<span style='color: #FFD93D;'>KST {kst_dt.strftime('%H:%M')}</span> ({diff_str})")
        self.info_label.setText(txt)
    
    def closeEvent(self, event):
        # When user clicks the X or uses Alt+F4, just hide
        event.ignore()
        self.hide()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

class SystemTrayApp(QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        super().__init__(icon, parent)
        self.window = MainWindow()
        
        # Standard QMenu for System Tray
        self.menu = QMenu()
        
        # Open (열기)
        action_open = QAction("열기", self)
        action_open.triggered.connect(self.show_window)
        self.menu.addAction(action_open)
        
        self.menu.addSeparator()

        # Exit (종료)
        action_exit = QAction("종료", self)
        action_exit.triggered.connect(QApplication.quit) # Immediate exit
        self.menu.addAction(action_exit)
        
        # Set Context Menu - This automatically handles right-click UX
        self.setContextMenu(self.menu)
        
        # Hook activation for Left-click or Double-click
        self.activated.connect(self.on_activated)

    def on_activated(self, reason):
        # Slack/Discord style: Left-click (Trigger) or Double-click shows window
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            if self.window.isHidden():
                self.show_window()
            else:
                self.window.hide()

    def show_window(self):
        self.window.refresh_timeline()
        self.window.show()
        self.window.activateWindow()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Single Instance Check
    app_id = "UTCtoKST_SingleInstance_Lock"
    socket = QLocalSocket()
    socket.connectToServer(app_id)
    if socket.waitForConnected(500):
        # Already running. Optional: could send a message to show window.
        sys.exit(0)

    app.setQuitOnLastWindowClosed(False)
    
    # Generic icon
    from PyQt5.QtGui import QPixmap, QPainter, QColor
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setBrush(QColor("#4ECDC4"))
    painter.drawEllipse(2, 2, 28, 28)
    painter.end()
    
    icon = QIcon(pixmap)
    
    tray = SystemTrayApp(icon)
    
    # Single Instance Server: Listen for new attempts and show window
    server = QLocalServer()
    server.listen(app_id)
    server.newConnection.connect(tray.show_window)
    
    tray.show()
    
    # Initial show
    tray.show_window()
    
    sys.exit(app.exec_())
