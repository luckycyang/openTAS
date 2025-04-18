import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Pane {
    ColumnLayout {
        anchors.fill: parent
        
        SideButton { text: "STT" }
        SideButton { text: "TTS" }
        SideButton { text: "Models management"}
        SideButton { text: "Log" }
        // Non-exhaust

        // Blank block at the bottom
        Rectangle {
            Layout.preferredHeight: parent.height * 0.4
        }
    }
}
