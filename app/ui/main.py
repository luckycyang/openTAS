import sys
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuick import QQuickView

class App():
    _app: QGuiApplication
    _view: QQuickView
    
    def __init__(self) -> None:
        self._app = QGuiApplication(sys.argv)
        self._view = QQuickView()

        self._view.engine().quit.connect(self._app.exit)        
        self._view.setSource('app/ui/qml/main.qml')

        self._view.show()
    
    def run(self):
        print("App is running...")
        return self._app.exec()

if __name__ == "__main__":
    app = App()
    exit_code = app.run()
    sys.exit(exit_code)
