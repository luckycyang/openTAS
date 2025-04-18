import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

ApplicationWindow {
    id: main
    width: 800
    height: 800
    visible: true
    title: "OpenTAS"

    RowLayout {
        anchors.fill: parent
        
        Sidebar {
            Layout.fillHeight: true
            Layout.preferredWidth: parent.width * 0.2
            targetLoader: loader
        }

        Loader {
            id: loader
            Layout.fillHeight: true
            Layout.fillWidth: true
            source: "Stt.qml"
        }
    }
}
