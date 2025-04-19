pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt.labs.qmlmodels
import QtQuick.Dialogs

Pane {
    id: root

    property string output
    property var model: TableModel {
        TableModelColumn { display: "hotWord" }
        TableModelColumn { display: "weight" }

        rows: [
            { "hotWord": "apple", "weight": 20 },
        ]
    }
    property string serverAddress
    property string asrMode: "2pass"
    property bool itnEnable: true
    property bool connected: false
    property bool useRecorder: true
    property string recordFile

    SttBridge {
        id: bridge
    }

    Column {
        anchors.fill: parent
        spacing: parent.height * 0.04

        // Top padding
        Item {
            width: parent.width
            height: parent.height * 0.03
        }
        
        // Server address
        RowLayout {
            width: parent.width
            state: root.connected ? "connected" : "unconnected"
            states: [
                State {
                    name: "unconnected"
                    PropertyChanges {
                        target: serverAddressInput; enabled: true
                    }
                    PropertyChanges { target: connectedIcon; text: "   " }
                },
                State {
                    name: "connected"
                    PropertyChanges {
                        target: serverAddressInput; enabled: false
                    }
                    PropertyChanges { target: connectedIcon; text: "✅" }
                }
            ]
            
            Text {
                text: qsTr("Asr server address(required)")
            }
            
            TextField {
                id: serverAddressInput
                placeholderText: qsTr("Enter target server here")
                Layout.fillWidth: true
                text: root.serverAddress
            }

            Text {
                id: connectedIcon
                text: "   "
            }
        }

        // Microphone mode
        RowLayout {
            CheckBox {
                text: qsTr("Use microphone")
                checked: true
                onClicked: {
                    root.useRecorder = checked
                    root.recordFile = ""
                }
            }

            Button {
                visible: !root.useRecorder
                text: qsTr("Pick record file")
                onClicked: filePicker.open()
            }

            Text {
                text: root.recordFile
                visible: !root.useRecorder
            }

            FileDialog {
                id: filePicker
                onAccepted: root.recordFile = selectedFile
            }
        }
        
        // Model mode and Itn
        RowLayout {
            width: parent.width * 0.95
            visible: root.useRecorder

            Text {
                text: qsTr("Model mode")
            }

            RadioButton {
                text: "2pass"
                checked: true

                onClicked: root.asrMode = "2pass"
            }

            RadioButton {
                text: "online"

                onClicked: root.asrMode = "online"
            }

            RadioButton {
                text: "offline"

                onClicked: root.asrMode = "offline"
            }

            // Delimiter
            Rectangle {
                Layout.preferredHeight: parent.height * 0.8
                Layout.preferredWidth: parent.width * 0.007
                color: "black"
            }

            CheckBox {
                text: "Itn"
                checked: true

                onClicked: root.itnEnable = checked
            }
        }

        // Hot words
        ColumnLayout {
            id: hotWordArea
            width: parent.width * 0.9
            height: parent.height * 0.2

            HorizontalHeaderView {
                syncView: tableView
                clip: true
                interactive: false
                model: [ qsTr("Hot word"), qsTr("Weight") ]
                resizableColumns: false
            }
            
            TableView {
                id: tableView
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                flickableDirection: Flickable.VerticalFlick

                model: root.model

                delegate: Rectangle {
                    id: cell
                    implicitWidth: hotWordArea.width * 0.4
                    implicitHeight: hotWordArea.height * 0.15
                    border.color: "lightgrey"

                    required property string display

                    Text {
                        anchors.centerIn: parent
                        text: cell.display
                    }

                    TableView.editDelegate: TextField {
                        anchors.fill: parent
                        text: cell.display
                        horizontalAlignment: TextInput.AlignHCenter
                        verticalAlignment: TextInput.AlignVCenter

                        Component.onCompleted: selectAll()
                        TableView.onCommit: cell.display = text
                    }
                }
            }

            Button {
                text: qsTr("Add new hot word")
                onClicked: root.model.appendRow({
                    "hotWord": "", "weight": 0
                })
            }
        }

        RowLayout {
            Button {
                text: qsTr("Connect")

                onClicked: {
                    root.connected = true
                }
            }

            Button {
                text: qsTr("Start")
            }

            Button {
                text: qsTr("Finish")

                onClicked: {
                    root.connected = false
                }
            }
        }

        // Output
        ColumnLayout {
            Text {
                text: qsTr("Output")
            }

            ScrollView {
                Layout.fillHeight: true
                Layout.fillWidth: true
                
                TextArea {
                    text: root.output
                    placeholderText: qsTr("None")
                    readOnly: true
                }
            }
        }
    }
}
