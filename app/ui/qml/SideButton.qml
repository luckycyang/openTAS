import QtQuick
import QtQuick.Layouts

Rectangle {
    property string text
    
    Layout.fillWidth: true
    Layout.fillHeight: true
    color: "lightgrey"

    Text {
        text: parent.text
        anchors.centerIn: parent
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true

        onEntered: {
            parent.color = "grey"
        }

        onExited: {
            parent.color = "lightgrey"
        }
    }
}
