import sys
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

class App():
    _qt_app: QGuiApplication
    _engine: QQmlApplicationEngine
    
    def __init__(self) -> None:
        self._qt_app = QGuiApplication(sys.argv)
        self._engine = QQmlApplicationEngine()

        self._engine.load('app/ui/qml/Main.qml')
        self._engine.quit.connect(self._qt_app.exit)
    
    def run(self):
        print('App is running...')
        return self._qt_app.exec()

if __name__ == "__main__":
    app = App()
    exit_code = app.run()
    sys.exit(exit_code)
