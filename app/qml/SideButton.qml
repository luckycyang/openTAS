import QtQuick
import QtQuick.Layouts

Rectangle {
    id: root
    Layout.fillWidth: true
    Layout.fillHeight: true
    color: "#f0f0f0"
    state: selected ? "selected" : (hovered ? "hovered" : "normal")
    states: [
        State {
            name: "normal"
            PropertyChanges { target: root; color: "#f0f0f0" }
        },
        State {
            name: "hovered"
            PropertyChanges { target: root; color: "#d1d1d1" }
        },
        State {
            name: "selected"
            PropertyChanges { target: root; color: "#a0a0a0" }
            PropertyChanges { target: leftBorder; visible: true }
            PropertyChanges { target: buttonText; font.bold: true }
        }
    ]

    property string text
    property string targetQml
    property bool hovered: false
    property bool selected: false


    Text {
        id: buttonText
        text: qsTr(parent.text)
        anchors.centerIn: parent
    }

    Rectangle {
        id: leftBorder
        anchors.left: parent.left
        width: parent.width * 0.01
        height: parent.height
        color: "black"
        visible: false
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true

        onEntered: root.hovered = true
        onExited: root.hovered = false
        onClicked: root.clicked()
    }

    signal clicked()
}
