import sys
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from bridge import *

class App():
    qt_app: QGuiApplication
    engine: QQmlApplicationEngine
    
    def __init__(self) -> None:
        self.qt_app = QGuiApplication(sys.argv)
        self.engine = QQmlApplicationEngine()

        self.engine.load('app/qml/Main.qml')
        self.engine.quit.connect(self.qt_app.exit)
    
    def run(self) -> int:
        return self.qt_app.exec()

if __name__ == "__main__":
    app = App()
    sys.exit(app.run())
