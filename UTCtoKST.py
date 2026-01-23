import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QSystemTrayIcon, QMenu, 
                             QAction, QVBoxLayout, QWidget, QScrollArea, QLabel, 
                             QHBoxLayout, QPushButton)
from PyQt5.QtCore import Qt, QTimer, QDateTime, QTime
from PyQt5.QtGui import QIcon, QFont, QCursor
from PyQt5.QtNetwork import QLocalServer, QLocalSocket

import utils
from ui_components import TimelineContainer
from alarm_controller import AlarmController
from alarm_toggle_button import AlarmToggleButton
from alarm_settings_dialog import AlarmSettingsDialog
from tray_alarm_popup import TrayAlarmPopup

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UTC <-> KST Converter")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(800, 340)
        
        # Stylesheet
        self.setStyleSheet("""
            QMainWindow { background-color: transparent; border: none; }
            QLabel { color: white; font-family: 'Segoe UI'; }
            QScrollArea { border: none; background: transparent; }
            QWidget#centralWidget {
                 background-color: #2C3E50;
                 border-radius: 10px;
            }
        """)
        
        self.alarm_controller = AlarmController(self)
        self.alarm_controller.alarm_triggered.connect(self.on_alarm_triggered)
        
        self.init_ui()
        self.init_timer()
        
        # --- Apply Initial Persisted State ---
        self.alarm_btn.setChecked(self.alarm_controller.enabled)
        # Timeline index will be applied after first populate in refresh_timeline

    def init_ui(self):
        self.central_widget = QWidget()
        self.central_widget.setObjectName("centralWidget")
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # --- Top Bar ---
        self.top_bar = QWidget()
        self.top_bar.setStyleSheet("background-color: rgba(0,0,0,0.2); border-top-left-radius: 10px; border-top-right-radius: 10px;")
        self.top_hbox = QHBoxLayout(self.top_bar)
        
        self.lbl_datetime = QLabel("Date Time")
        self.lbl_datetime.setFont(QFont("Segoe UI", 10))
        self.top_hbox.addWidget(self.lbl_datetime)
        self.top_hbox.addStretch()

        # Alarm Toggle
        self.alarm_btn = AlarmToggleButton()
        self.alarm_btn.toggled.connect(self.alarm_controller.set_enabled)
        self.top_hbox.addWidget(self.alarm_btn)
        
        # Alarm Settings
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setFixedSize(32, 32)
        self.settings_btn.setToolTip("Alarm Settings")
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                color: white; background-color: transparent; border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 16px; font-size: 16px; line-height: 1;
            }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.1); }
        """)
        self.settings_btn.clicked.connect(self.open_alarm_settings)
        self.top_hbox.addWidget(self.settings_btn)

        self.top_hbox.addSpacing(10)
        
        self.btn_close = QPushButton("X")
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.setStyleSheet("""
            QPushButton { color: white; background: transparent; font-weight: bold; border: none; }
            QPushButton:hover { color: #FF6B6B; }
        """)
        self.btn_close.clicked.connect(self.hide)
        self.top_hbox.addWidget(self.btn_close)
        
        self.layout.addWidget(self.top_bar)
        
        # --- Info Bar ---
        self.info_label = QLabel("Select a time slot.")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setFont(QFont("Segoe UI", 12))
        self.info_label.setStyleSheet("color: #FFD93D; background-color: #2C3E50; padding: 5px;")
        self.layout.addWidget(self.info_label)

        # --- Timeline ---
        class HorizontalScrollArea(QScrollArea):
             def wheelEvent(self, event):
                 if event.angleDelta().y() != 0:
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
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{ border: none; background: transparent; }}
            QScrollBar:horizontal {{ border: none; background: {utils.COLOR_TIMELINE_BG}; height: 8px; margin: 0; }}
            QScrollBar::handle:horizontal {{ background: #4CA1AF; min-width: 20px; border-radius: 4px; }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; background: none; }}
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background: none; }}
        """)
        
        self.timeline = TimelineContainer()
        self.timeline.slot_selected.connect(self.on_slot_selected)
        
        self.scroll_area.setWidget(self.timeline)
        self.layout.addWidget(self.scroll_area)
        
        self.refresh_timeline()

    def init_timer(self):
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
        now_utc = utils.get_current_time_utc().replace(minute=0, second=0, microsecond=0)
        self.timeline.populate(now_utc)
        
        # Restore saved selection index (or 0)
        saved_idx = self.alarm_controller.selected_time_index
        # Ensure index is within range of what was just populated
        if 0 <= saved_idx < 24:
            self.timeline.select_index(saved_idx)
        else:
            self.timeline.select_index(0)

    def on_slot_selected(self, utc_dt, kst_dt, index):
        """Handle selection and PERSIST the state."""
        # Visual Update
        self.update_info_text(utc_dt, kst_dt)
        
        # Persist Selection to Controller
        target_qtime = QTime(kst_dt.hour, kst_dt.minute)
        self.alarm_controller.set_target_time(target_qtime, index)

    def update_info_text(self, utc_dt, kst_dt):
        now_utc = utils.get_current_time_utc().replace(tzinfo=utils.UTC_TZ)
        utc_dt = utc_dt.replace(tzinfo=utils.UTC_TZ)
        diff = utc_dt - now_utc
        total_seconds = diff.total_seconds()
        
        if abs(total_seconds) < 60:
            diff_str = "<span style='color: #FF6B6B;'>Right Now</span>"
        else:
            is_future = total_seconds > 0
            secs = abs(int(total_seconds))
            hours = secs // 3600
            minutes = (secs % 3600) // 60
            time_parts = []
            if hours > 0: time_parts.append(f"{hours} hours")
            if minutes > 0: time_parts.append(f"{minutes} min")
            time_txt = " ".join(time_parts) if time_parts else "0 min"
            diff_str = f"<span style='color: #4ECDC4;'>in {time_txt}</span>" if is_future else f"<span style='color: #95A5A6;'>{time_txt} ago</span>"
            
        txt = f"Selected: <span style='color: #FFD93D;'>UTC {utc_dt.strftime('%H:%M')}</span> | <span style='color: #FFD93D;'>KST {kst_dt.strftime('%H:%M')}</span> ({diff_str})"
        self.info_label.setText(txt)

    def open_alarm_settings(self):
        dialog = AlarmSettingsDialog(self.alarm_controller, self)
        dialog.exec_()

    def on_alarm_triggered(self, message):
        """Handle alarm trigger: Show custom popup. Note: No longer auto-disables the toggle."""
        # User requested persistence, so we keep the toggle ARMED (True) if they want repeating.
        # If they want it off, they toggle manually.
        self.popup = TrayAlarmPopup(message)
        self.popup.show()
    
    def closeEvent(self, event):
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
        self.menu = QMenu()
        
        action_open = QAction("열기", self)
        action_open.triggered.connect(self.show_window)
        self.menu.addAction(action_open)
        self.menu.addSeparator()
        action_exit = QAction("종료", self)
        action_exit.triggered.connect(QApplication.quit)
        self.menu.addAction(action_exit)
        
        self.setContextMenu(self.menu)
        self.activated.connect(self.on_activated)

    def on_activated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            if self.window.isHidden():
                self.show_window()
            else:
                self.window.hide()

    def show_window(self):
        # Only refresh if necessary, or just show
        self.window.show()
        self.window.activateWindow()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app_id = "UTCtoKST_SingleInstance_Lock"
    socket = QLocalSocket()
    socket.connectToServer(app_id)
    if socket.waitForConnected(500):
        sys.exit(0)

    app.setQuitOnLastWindowClosed(False)
    
    # Generic icon
    from PyQt5.QtGui import QPixmap, QPainter, QColor
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setFont(QFont("Segoe UI Emoji", 18))
    painter.drawText(pixmap.rect().adjusted(1,1,-1,-1), Qt.AlignCenter, "🕒")
    painter.end()
    
    icon = QIcon(pixmap)
    app.setWindowIcon(icon)
    
    tray = SystemTrayApp(icon)
    server = QLocalServer()
    server.listen(app_id)
    server.newConnection.connect(tray.show_window)
    
    tray.show()
    tray.show_window()
    sys.exit(app.exec_())
