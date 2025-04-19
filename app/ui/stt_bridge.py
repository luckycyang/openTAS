from PySide6.QtCore import QObject
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "io.qt.textproperties"

@QmlElement
class SttBridge(QObject):
    pass
