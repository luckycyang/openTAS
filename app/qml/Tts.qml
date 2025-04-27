pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import QtCore

import bridge.tts 1

Pane {
    id: root
    anchors.fill: parent

    property string input
    property ListModel audioList: ListModel {
        ListElement {
            filename: "example.wav"
            url: "example.com"
        }
    }
    property string voice
    property int voiceValue
    property int textSeed
    property string prompt
    property bool skipRefine
    property int inferToken: 2048
    property int refineToken: 384
    property int speed
    property double temperature
    property double topP
    property double topK
    property string ttsServerAddress

    TtsBridge { id: bridge }

    Connections {
        target: bridge

        function onReceived(audioList) {
            for (var audioInfo of audioList) {
                root.audioList.append({
                    "filename": audioInfo.filename,
                    "url": audioInfo.url,
                })
            }

            synthesizeButton.enabled = true
        }
    }

    Settings {
        id: settings

        property alias voice: root.voice
        property alias voiceValue: root.voiceValue
        property alias textSeed: root.textSeed
        property alias prompt: root.prompt
        property alias skipRefine: root.skipRefine
        property alias inferToken: root.inferToken
        property alias refineToken: root.refineToken
        property alias speed: root.speed
        property alias temperature: root.temperature
        property alias topP: root.topP
        property alias topK: root.topK
        property alias ttsServerAddress: root.ttsServerAddress
    }

    Component.onCompleted: root.audioList.remove(0)

    Column {
        anchors.fill: parent
        spacing: root.height * 0.04

        Item {
            width: parent.width
            height: parent.height * 0.04
        }

        // Server address...
        RowLayout {
            width: parent.width * 0.8

            Text {
                text: qsTr("Server address(required)")
            }

            TextField {
                text: root.ttsServerAddress
                Layout.fillWidth: true

                onTextChanged: root.ttsServerAddress = text
            }
        }

        // Input
        ScrollView {
            width: parent.width * 0.95
            height: parent.height * 0.15

            TextArea {
                text: root.input
                placeholderText:
                    qsTr("Text to be converted here, splited by line")
                anchors.fill: parent

                onTextChanged: root.input = text
            }
        }

        RowLayout {
            width: parent.width
            
            Button {
                id: synthesizeButton
                text: qsTr("Synthesize voice")

                onClicked: {
                    enabled = false
                    bridge.start(root.ttsServerAddress, {
                        "text": root.input,
                        "prompt": root.prompt,
                        "voice": root.voice,
                        "speed": root.speed,
                        "temperature": root.temperature,
                        "top_p": root.topP,
                        "top_k": root.topK,
                        "refine_token": root.refineToken,
                        "infer_token": root.inferToken,
                        "seed": root.textSeed,
                        "skip_refine": root.skipRefine,
                        "custom_voice": root.voiceValue,
                    })
                }
            }

            Button {
                text: qsTr("Import txt")

                onClicked: inputFilePicker.open()
            }

            FileDialog {
                id: inputFilePicker

                onAccepted: root.input = bridge.import_text(selectedFile)
            }
        }

        // Advanced options
        Text {
            text: qsTr("Advanced options")
        }
        
        RowLayout {
            width: parent.width * 0.9

            LabeledTextInput {
                display: qsTr("Select voice")
                input: root.voice

               onModified: function(text) {
                    root.voice = text
                }
            }

            LabeledTextInput {
                display: qsTr("Voice value")
                input: root.voiceValue
                validator: IntValidator {}

                onModified: function(text) {
                    root.voiceValue = text
                }
            }

            LabeledTextInput {
                display: qsTr("Text seed")
                input: root.textSeed
                validator: IntValidator {}

                onModified: function(text) {
                    root.textSeed = text
                }
            }
        }
        
        RowLayout {
            LabeledTextInput {
                display: qsTr("Prompt")
                input: root.prompt

                onModified: function(text) {
                    root.prompt = text
                }
            }

            LabeledTextInput {
                display: qsTr("Infer token")
                input: root.inferToken
                validator: IntValidator {}

                onModified: function(text) {
                    root.inferToken = text
                }
            }
        }

        // Refine
        RowLayout {
            width: parent.width * 0.6
            
            CheckBox {
                text: qsTr("Skip refine text")
                onClicked: root.skipRefine = checked
            }

            LabeledTextInput {
                display: qsTr("Refine token")
                input: root.refineToken
                validator: IntValidator {}
                visible: !root.skipRefine

                onModified: function(text) {
                    root.refineToken = text
                }
            }
        }

        RowLayout {
            width: parent.width

            LabeledTextInput {
                display: qsTr("Speed")
                input: root.speed
                validator: IntValidator {}

                onModified: function(text) {
                    root.speed = text
                }
            }

            LabeledTextInput {
                display: qsTr("Temperature")
                input: root.temperature
                validator: DoubleValidator {}

                onModified: function(text) {
                    root.temperature = text
                }
            }

            LabeledTextInput {
                display: qsTr("Top P")
                input: root.topP
                validator: DoubleValidator {}

                onModified: function(text) {
                    root.topP = text
                }
            }

            LabeledTextInput {
                display: qsTr("Top K")
                input: root.topK
                validator: DoubleValidator {}

                onModified: function(text) {
                    root.topK = text
                }
            }
        }

        // Output
        Text {
            text: qsTr("Output")
        }

        ListView {
            width: parent.width * 0.8
            height: parent.height * 0.15
            
            model: root.audioList

            delegate: RowLayout {
                width: ListView.view.width

                required property string filename
                required property string url

                Text {
                    text: parent.filename
                    elide: Text.ElideLeft
                    Layout.fillWidth: true
                }

                Button {
                    text: qsTr("Download")

                    onClicked: outputPicker.open()
                }

                FileDialog {
                    id: outputPicker
                    fileMode: FileDialog.SaveFile

                    onAccepted: bridge.export(url, selectedFile)
                }
            }
        }
    }
}
