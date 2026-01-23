from PyQt5.QtCore import QObject, QTimer, QTime, pyqtSignal, QSettings

DEFAULT_ALARM_MESSAGE = "⏰ 설정된 시간이 되었습니다"
DEFAULT_PRESETS = [
    "⏰ 설정된 시간이 되었습니다",
    "회의 시작 알림!",
    "휴식 시간입니다!"
]

class AlarmController(QObject):
    """
    Central authority for all alarm logic and persistent state.
    Maintains presets, active selection, enabled state, and target time index.
    """
    alarm_triggered = pyqtSignal(str)
    state_changed = pyqtSignal() # Optional: Signal for UI to update if state changes internally

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings("Antigravity", "UTCtoKST")
        
        # 1. Enabled State
        self.enabled = self.settings.value("alarm_enabled", False, type=bool)
        
        # 2. Presets & Active Selection
        self.presets = []
        for i in range(3):
            val = self.settings.value(f"alarm_preset_{i+1}", DEFAULT_PRESETS[i])
            self.presets.append(val)
        self.active_preset_index = int(self.settings.value("active_preset_index", 0))
        
        # 3. Time Selection Persistence
        # Store index of the selected time slot (relative to current window view)
        self.selected_time_index = int(self.settings.value("selected_time_index", 0))
        self.target_time = None # Set by MainWindow based on selected_time_index
        
        # Internal logical message
        self.message = self.presets[self.active_preset_index]
        self._triggered_once = False

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._check_time)
        self.timer.start(1000)

    def set_enabled(self, value):
        self.enabled = value
        self.settings.setValue("alarm_enabled", value)
        if not value:
            self._triggered_once = False
        self.state_changed.emit()

    def set_target_time(self, time, index=0):
        """Update target time and the persisted selection index."""
        self.target_time = time
        self.selected_time_index = index
        self.settings.setValue("selected_time_index", index)
        self._triggered_once = False # Reset trigger whenever time changes
        self.state_changed.emit()

    def set_active_preset(self, index, message):
        """Update active preset index and its custom message."""
        if 0 <= index < 3:
            self.active_preset_index = index
            self.presets[index] = message
            self.message = message
            
            self.settings.setValue(f"alarm_preset_{index+1}", message)
            self.settings.setValue("active_preset_index", index)
            self.state_changed.emit()

    def get_preset_message(self, index):
        if 0 <= index < 3:
            return self.presets[index]
        return DEFAULT_ALARM_MESSAGE

    def reset_preset(self, index):
        """Restore default for a specific preset and update active if it was the one."""
        if 0 <= index < 3:
            default_msg = DEFAULT_PRESETS[index]
            self.presets[index] = default_msg
            self.settings.setValue(f"alarm_preset_{index+1}", default_msg)
            
            if self.active_preset_index == index:
                self.message = default_msg
            
            self.state_changed.emit()
            return default_msg
        return DEFAULT_ALARM_MESSAGE

    def _check_time(self):
        if not self.enabled or not self.target_time:
            return

        now = QTime.currentTime()
        
        # Trigger only at the exact HH:mm
        if (not self._triggered_once and 
            now.hour() == self.target_time.hour() and 
            now.minute() == self.target_time.minute()):
            
            self._triggered_once = True
            # Re-confirm enabled logic: User wants "자동 해제 없음" (No auto-off) 
            # but usually single alarms should stop firing once matched.
            # We'll emit but leave 'enabled' alone so it hits again next day or stays visible in UI.
            self.alarm_triggered.emit(self.message)
            
            # To prevent firing every second of the minute, we mark as triggered.
            # It resets when a new time is selected or enabled is toggled.
