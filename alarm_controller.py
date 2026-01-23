from PyQt5.QtCore import QObject, QTimer, QTime, pyqtSignal, QSettings

DEFAULT_ALARM_MESSAGE = "⏰ 설정된 시간이 되었습니다"
DEFAULT_PRESETS = [
    "⏰ 설정된 시간이 되었습니다",
    "회의 시작 알림!",
    "휴식 시간입니다!"
]

class AlarmController(QObject):
    """
    Handles alarm logic: monitoring time and emitting trigger signals with messages.
    Source of truth for all 3 presets and the active selection.
    """
    alarm_triggered = pyqtSignal(str) # Emit the message string

    def __init__(self, parent=None):
        super().__init__(parent)
        self.enabled = False
        self.target_time = None 
        
        # Persistence Logic
        self.settings = QSettings("Antigravity", "UTCtoKST")
        
        # 1. Load Presets
        self.presets = []
        for i in range(3):
            val = self.settings.value(f"alarm_preset_{i+1}", DEFAULT_PRESETS[i])
            self.presets.append(val)
            
        # 2. Load Active Preset Index
        self.active_preset_index = int(self.settings.value("active_preset_index", 0)) # Default to 1st preset
        
        # 3. Load Current Message (Always sync with selected preset on startup)
        self.message = self.presets[self.active_preset_index]

        self._triggered_once = False

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._check_time)
        self.timer.start(1000)

    def set_enabled(self, value):
        self.enabled = value
        if not value:
            self._triggered_once = False

    def set_target_time(self, time):
        self.target_time = time
        self._triggered_once = False

    def set_active_preset(self, index, message):
        """Update a specific preset and make it the active one."""
        if 0 <= index < 3:
            self.active_preset_index = index
            self.presets[index] = message
            self.message = message
            
            # Persist to settings
            self.settings.setValue(f"alarm_preset_{index+1}", message)
            self.settings.setValue("active_preset_index", index)

    def get_preset_message(self, index):
        if 0 <= index < 3:
            return self.presets[index]
        return DEFAULT_ALARM_MESSAGE

    def reset_preset(self, index):
        """Restore default message for a specific preset."""
        if 0 <= index < 3:
            default_msg = DEFAULT_PRESETS[index]
            self.set_active_preset(index, default_msg)
            return default_msg
        return DEFAULT_ALARM_MESSAGE

    def _check_time(self):
        if not self.enabled or not self.target_time:
            return

        now = QTime.currentTime()
        
        if (not self._triggered_once and 
            now.hour() == self.target_time.hour() and 
            now.minute() == self.target_time.minute()):
            
            self._triggered_once = True
            self.enabled = False
            self.alarm_triggered.emit(self.message)
