# app/bridge/models_bridge.py
import subprocess
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtQml import QmlElement

from ..models import ModelManager

QML_IMPORT_NAME = "bridge.models"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class ModelsBridge(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.manager = ModelManager()

    @Slot(result=list)
    def getAllModels(self) -> list:
        return self.manager.get_all_model_names()

    @Slot(str, result=str)
    def getContainerStatus(self, name: str) -> str:
        return self.manager.get_model_status(name)

    @Slot(str)
    def startContainer(self, name: str):
        self.manager.start_model(name)

    @Slot(str)
    def stopContainer(self, name: str):
        self.manager.stop_model(name)