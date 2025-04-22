pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import QtCore

import bridge.stt 1

Pane {
    id: root

    property string output
    property string serverAddress
    property string asrMode: "2pass"
    property bool itnEnable
    property bool useRecorder
    property string recordFile
    property string hotWords
    property bool sslEnable
    property int audioFormatChosen
    property string chunkSize
    property int chunkInterval
    property var microphones
    property var microphoneNames
    property int microphoneChosen
    property int channels
    property int rate
    property double timeout

    SttBridge { id: bridge }

    Connections {
        target: bridge

        function onReceived(s) {
            root.output += s
        }

        function onServiceStopped() {
            startButton.enabled = true
            finishButton.enabled = false
        }
    }

    Component.onCompleted: {
        // Get system microphones and fill the combo box
        let infos = bridge.send_microphone_infos()

        var names = []
        for (var i = 0; i < infos.length; ++i) {
            names.push(infos[i].name)
        }

        root.microphones = infos
        root.microphoneNames = names
    }

    // Cache what user inputed
    Settings {
        id: settings
        category: "stt"

        property alias serverAddress: root.serverAddress
        property alias asrMode: root.asrMode
        property alias itnEnabled: root.itnEnable
        property alias useRecorder: root.useRecorder
        property alias hotWords: root.hotWords
        property alias sslEnable: root.sslEnable
        property alias audioFormatIndex: root.audioFormatChosen
        property alias chunkSize: root.chunkSize
        property alias chunkInterval: root.chunkInterval
        property alias channels: root.channels
        property alias rate: root.rate
        property alias timeout: root.timeout
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

            Text {
                text: qsTr("Asr server address(required)")
            }
            
            TextField {
                id: serverAddressInput
                placeholderText: qsTr("Enter target server here")
                Layout.fillWidth: true
                text: root.serverAddress

                onTextChanged: root.serverAddress = text
            }

            CheckBox {
                text: "Ssl"
                checked: root.sslEnable
                onClicked: root.sslEnable = checked
            }
        }

        // Microphone mode
        RowLayout {
            width: parent.width
            
            CheckBox {
                text: qsTr("Use microphone")
                checked: root.useRecorder
                onClicked: {
                    root.useRecorder = checked
                    root.recordFile = ""
                }
            }

            // Microphone picker
            ComboBox {
                id: microphonePicker
                model: root.microphoneNames
                visible: root.useRecorder

                onActivated: root.microphoneChosen = currentIndex
            }
        }
        
        // Audio options
        RowLayout {
            width: parent.width
            
            Text {
                text: qsTr("Format")
                visible: root.useRecorder
            }

            ComboBox {
                id: formatPicker
                model: [
                    "Int8", "Int16", "Int24", "Int32",
                    "Float32", "UInt8"
                ]
                visible: root.useRecorder
                currentIndex: root.audioFormatChosen

                onActivated: root.audioFormatChosen = currentIndex
            }

            Text {
                text: qsTr("Channels")
                visible: root.useRecorder
            }

            TextField {
                text: root.channels
                visible: root.useRecorder
                validator: IntValidator {}

                onTextChanged: root.channels = text
            }

            Text {
                text: qsTr("Rate")
                visible: root.useRecorder
            }

            TextField {
                text: root.rate
                visible: root.useRecorder
                validator: IntValidator {}
                
                onTextChanged: root.rate = text
            }
                        
            // If not use microphone
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
                checked: root.asrMode === "2pass"

                onClicked: root.asrMode = "2pass"
            }

            RadioButton {
                text: "online"
                checked: root.asrMode === "online"

                onClicked: root.asrMode = "online"
            }

            RadioButton {
                text: "offline"
                checked: root.asrMode === "offline"

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
                checked: root.itnEnable

                onClicked: root.itnEnable = checked
            }
        }

        RowLayout {
            Text {
                text: qsTr("Chunk size")
            }

            TextField {
                text: root.chunkSize
                placeholderText: "0, 60, 8"
                validator: RegularExpressionValidator {
                    regularExpression: /[0-9]+,[0-9]+,[0-9]+/
                }

                onTextChanged: root.chunkSize = text
            }

            Text {
                text: qsTr("Chunk interval")
            }

            TextField {
                text: root.chunkInterval
                validator: IntValidator {}

                onTextChanged: root.chunkInterval = text
            }

            Text {
                text: qsTr("Timeout")
            }

            TextField {
                text: root.timeout
                validator: DoubleValidator {}

                onTextChanged: root.timeout = text
            }
        }

        // Hot words
        ColumnLayout {
            width: parent.width * 0.8
            height: parent.height * 0.2

            Text {
                text: qsTr("Hot words")
            }

            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true

                TextArea {
                    placeholderText: "apple 20\nbanana 40"
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    onEditingFinished: root.hotWords = text
                    wrapMode: TextArea.Wrap
                    text: root.hotWords
                }
            }
        }            
        
        RowLayout {
            Button {
                id: startButton
                text: qsTr("Start")
                enabled: true

                onClicked: {
                    enabled = false
                    finishButton.enabled = true
                    exportButton.enabled = false
                
                    let info = root.microphones[root.microphoneChosen]
                
                    bridge.start({
                        "server_address": root.serverAddress,
                        "ssl_enable": root.sslEnable,
                        "use_recorder": root.useRecorder,
                        "record_file": !root.useRecorder ?
                            root.recordFile : undefined,
                        "asr_mode": root.asrMode,
                        "itn_enable": root.itnEnable,
                        "hot_words": root.hotWords,
                        "audio_format":
                            formatPicker.textAt(root.audioFormatChosen),
                        "chunk_size": root.chunkSize,
                        "chunk_interval": root.chunkInterval,
                        "device_index":
                            root.microphones[root.microphoneChosen]
                                .device_index,
                        "channels": root.channels, 
                        "rate": root.rate,
                        "timeout": root.timeout,
                    })
                }
            }

            Button {
                id: finishButton
                text: qsTr("Finish")
                enabled: false

                onClicked: {
                    enabled = false
                    startButton.enabled = true
                    exportButton.enabled = true
                    
                    bridge.stop()
                }
            }

            Button {
                id: exportButton
                text: qsTr("Export")
                enabled: false

                onClicked: {
                    enabled = false
                
                    fileSaver.open()
                }
            }

            FileDialog {
                id: fileSaver
                fileMode: FileDialog.SaveFile

                onAccepted: bridge.save_output(selectedFile, root.output)
                onRejected: exportButton.enabled = true
            }
        }

        // Output
        ColumnLayout {
            width: parent.width * 0.95
            height: parent.height * 0.15
            
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
                    wrapMode: TextArea.Wrap
                }
            }
        }
    }
}
