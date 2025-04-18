pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Pane {
    id: root

    property string active: "STT"

    readonly property var buttons: [
        { text: "STT", targetQml: "Stt.qml" },
        { text: "TTS", targetQml: "Tts.qml" },
        { text: "Models management", targetQml: "ModelsManagement.qml"},
        { text: "Log", targetQml: "Log.qml" },
    ]
    required property Loader targetLoader

    ColumnLayout {
        anchors.fill: parent

        Repeater {
            model: root.buttons

            SideButton {
                required property var modelData
                text: modelData.text
                targetQml: modelData.targetQml
                selected: root.active === text
                onClicked: {
                    root.targetLoader.source = modelData.targetQml
                    root.active = modelData.text
                }
            }
        }
        
        // Blank block at the bottom
        Rectangle {
            Layout.preferredHeight: parent.height * 0.4
        }
    }
}
