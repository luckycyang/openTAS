from PySide6.QtCore import QObject,  Slot
from PySide6.QtQml import QmlElement
import os

from .utils import get_log_file_path

QML_IMPORT_NAME = "bridge.log"
QML_IMPORT_MAJOR_VERSION = 1

class LogReader(QObject):
    @Slot(result=str)
    def read_log(self):
        log_path = get_log_file_path()
        if not os.path.exists(log_path):
            return ""
        with open(log_path, "r", encoding="utf-8") as f:
            return f.read()
        
@QmlElement
class LogBridge(QObject):
    log_reader: LogReader

    def __init__(self):
        super().__init__()
        self.log_reader = LogReader()

    @Slot(result=str)
    def read_log(self):
        return self.log_reader.read_log()