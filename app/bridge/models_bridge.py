# app/bridge/models_bridge.py
import subprocess
from PySide6.QtCore import QObject, Signal, Slot, QTimer, QThreadPool, QRunnable
from PySide6.QtQml import QmlElement

from ..models import ModelManager

QML_IMPORT_NAME = "bridge.models"
QML_IMPORT_MAJOR_VERSION = 1

# 新增 Worker 类（放在 ModelsBridge 类之前）
class DockerWorker(QRunnable):
    def __init__(self, command, model_type, name, callback):
        super().__init__()
        self.command = command
        self.model_type = model_type
        self.name = name
        self.callback = callback

    def run(self):
        try:
            result = subprocess.run(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.callback(
                self.model_type,
                self.name,
                result.returncode == 0
            )
        except Exception as e:
            self.callback(self.model_type, self.name, False)

@QmlElement
class ModelsBridge(QObject):
    statusChanged = Signal(str, str, str)  # (model_type, name, status)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.manager = ModelManager()
        self.threadpool = QThreadPool.globalInstance()
        self._setup_auto_refresh()

    def _execute_async(self, command, model_type, name):
        # 通用异步执行方法
        worker = DockerWorker(
            command, 
            model_type,
            name,
            self._handle_operation_result
        )
        self.threadpool.start(worker)

    def _handle_operation_result(self, model_type: str, name: str, success: bool):
        if success:
            new_status = self.manager.get_model_status(model_type, name)
            self.statusChanged.emit(model_type, name, new_status)

    @Slot(str, str)
    def startContainer(self, model_type: str, name: str):
        self._execute_async(
            ["docker", "start", name], 
            model_type, 
            name
        )

    @Slot(str, str)
    def stopContainer(self, model_type: str, name: str):
        self._execute_async(
            ["docker", "stop", name], 
            model_type, 
            name
        )

    def _setup_auto_refresh(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._refresh_all_status)
        self.timer.start(5000)  # 每5秒自动刷新
        
    def _refresh_all_status(self):
        for model_type in ["stt", "tts"]:
            for name in self.manager.get_all_model_names_by_type(model_type):
                new_status = self.manager.get_model_status(model_type, name)
                self.statusChanged.emit(model_type, name, new_status)

    @Slot(str, str)
    def addModel(self, model_type: str, name: str):
        success = self.manager.add_model(model_type, name)
        print(f"[ModelsBridge] 添加模型 {'成功' if success else '失败'}: {model_type} - {name}")
        return success  # 返回操作结果
    @Slot(str, result=list)
    def getAllModelsByType(self, model_type: str) -> list:
        return self.manager.get_all_model_names_by_type(model_type)

    @Slot(str, str, result=str)
    def getContainerStatus(self, model_type: str, name: str) -> str:
        return self.manager.get_model_status(model_type, name)

    @Slot(str, str)
    def removeModel(self, model_type: str, name: str):
        """从 ModelManager 中移除模型引用"""
        try:
            # 调用 ModelManager 的移除方法
            success = self.manager.remove_model(model_type, name)
            if success:
                print(f"[ModelsBridge] 移除模型成功: {model_type} - {name}")
                self.statusChanged.emit(model_type, name, "not_exist")  # 更新状态为不存在
                return True
            else:
                print(f"[ModelsBridge] 移除模型失败: 模型 {name} 不存在")
                return False
        except Exception as e:
            print(f"[ModelsBridge] 移除模型异常: {e}")
            return False