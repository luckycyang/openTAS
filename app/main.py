import sys, os
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QCoreApplication

from .bridge import *

class App():
    qt_app: QGuiApplication
    engine: QQmlApplicationEngine
    
    def __init__(self) -> None:
        self.qt_app = QGuiApplication(sys.argv)
        self.engine = QQmlApplicationEngine()

        QCoreApplication.setOrganizationName("OpenTAS")
        QCoreApplication.setApplicationName("openTAS")

        self.engine.load('app/qml/Main.qml')
        self.engine.quit.connect(self.qt_app.exit)
    
    def run(self) -> int:
        return self.qt_app.exec()

if __name__ == "__main__":
    app = App()
    sys.exit(app.run())
