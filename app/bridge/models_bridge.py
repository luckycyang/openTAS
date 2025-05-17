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

    @Slot(str, str)
    def addModel(self, model_type: str, name: str):
        success = self.manager.add_model(model_type, name)
        if success:
            print(f"[ModelsBridge] 成功添加模型: {model_type} - {name}")
        else:
            print(f"[ModelsBridge] 添加模型失败或已存在: {model_type} - {name}")
    @Slot(str, result=list)
    def getAllModelsByType(self, model_type: str) -> list:
        print(f"getAllModelsByType: {model_type}")
        return self.manager.get_all_model_names_by_type(model_type)

    @Slot(str, str, result=str)
    def getContainerStatus(self, model_type: str, name: str) -> str:
        return self.manager.get_model_status(model_type, name)

    @Slot(str, str)
    def startContainer(self, model_type: str, name: str):
        self.manager.start_model(model_type, name)

    @Slot(str, str)
    def stopContainer(self, model_type: str, name: str):
        self.manager.stop_model(model_type, name)