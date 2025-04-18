import QtQuick
import QtQuick.Controls

ApplicationWindow {
    id: main
    height: 800
    width: 800
    visible: true
    title: "OpenTAS"

    Sidebar {
        height: parent.height
        width: parent.width * 0.3
    }
}
