import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Layouts 1.15

import bridge.models 1 

Rectangle {
    anchors.fill: parent

    function refreshModelList() {
        // 清空现有模型
        sttModelList.clear();
        ttsModelList.clear();

        // 重新加载 STT 模型
        var sttNames = modelsBridge.getAllModelsByType("stt");
        for (var i = 0; i < sttNames.length; i++) {
            sttModelList.append({ "name": sttNames[i], "type": "stt"});
        }

        // 重新加载 TTS 模型
        var ttsNames = modelsBridge.getAllModelsByType("tts");
        for (var i = 0; i < ttsNames.length; i++) {
            ttsModelList.append({ "name": ttsNames[i], "type": "tts" });
        }

        console.log("刷新后的 STT 模型:", sttNames);
        console.log("刷新后的 TTS 模型:", ttsNames);
    }

    // 公共的委托组件
    Component {
        id: modelDelegate

        Row {
            spacing: 20
            height: 40
            
            Text {
                text: "• " + (name || "未知")
                width: 100
                color: "black" // 强制颜色
                font.pixelSize: 14
            }

            Text {
                id: statusText
                text: "检查中..."
                width: 80

                function updateStatus() {
                    var status = modelsBridge.getContainerStatus(model.type, name);
                    statusText.text = status;
                }

                Component.onCompleted: {
                    console.log("name:", name);
                    updateStatus();
                }
            }

            Row {
                spacing: 10

                Button {
                    text: "启动"
                    onClicked: {
                        modelsBridge.startContainer(model.type, name)
                        statusText.updateStatus()
                    }
                }

                Button {
                    text: "停止"
                    onClicked: {
                        modelsBridge.stopContainer(model.type, name)
                        statusText.updateStatus()
                    }
                }

                Button {
                    text: "刷新"
                    onClicked: statusText.updateStatus()
                }
            }
        }
    }

    ModelsBridge {
        id: modelsBridge
    }

    ListModel {
        id: sttModelList
        ListElement { name: "funasr-online-server-cpu"; type: "stt" }
        ListElement { name: "whisper-cpu"; type: "stt" }
    }

    ListModel {
        id: ttsModelList
        ListElement { name: "chat-tts-ui-cpu"; type: "tts" }
        ListElement { name: "paddle-tts"; type: "tts" }
    }

    Component.onCompleted: {
        // 加载 STT 模型
        var sttNames = modelsBridge.getAllModelsByType("stt");
        for (var i = 0; i < sttNames.length; i++) {
            var modelName = sttNames[i];
            print("sttNames:", sttNames)
            sttModelList.append({ "name": modelName, "type": "stt" });
        }

        // 加载 TTS 模型
        var ttsNames = modelsBridge.getAllModelsByType("tts");
        for (var i = 0; i < ttsNames.length; i++) {
            var modelName = ttsNames[i];
            print("ttsNames:", ttsNames)
            ttsModelList.append({ "name": modelName, "type": "tts" });
        }
        
        
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 20
        
        Text {
            text: "本地模型管理"
            font.bold: true
            font.pixelSize: 20
        }

        Row {
            spacing: 10
            width: parent.width

            ComboBox {
                id: modelTypeComboBox
                model: ["stt", "tts"]
                currentIndex: 0
            }

            TextField {
                id: modelNameInput
                placeholderText: "输入模型名称"
                width: 200
            }

            Button {
                text: "添加模型"
                onClicked: {
                    var type = modelTypeComboBox.text;
                    var name = modelNameInput.text;
                    if (name) {
                        modelsBridge.addModel(type, name);
                        // 更新对应类型的列表
                        if (type === "stt") {
                            sttModelList.append({ "name": name, "type": "stt" });
                        } else if (type === "tts") {
                            ttsModelList.append({ "name": name, "type": "tts" });
                        }
                        modelNameInput.text = "";
                    }
                }
            }

            Button {
                text: "刷新列表"
                onClicked: {
                    refreshModelList();
                }
            }
        }


        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true
            
            Rectangle {
                anchors.fill: parent
                color: "#f0f0f0"
                radius: 5

                Column {
                    anchors.fill: parent
                    anchors.margins: 10

                    Text {
                        text: "STT 模型"
                        font.bold: true
                        font.pixelSize: 16
                    }

                    Item {
                        width: parent.width
                        height: parent.height

                        ListView {
                            clip: true
                            model: sttModelList
                            height: 100
                            delegate: modelDelegate

                            onContentHeightChanged: {
                                console.log("STT 列表项数量:", count);
                            }
                        }
                    }
                }
            }
        }

        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            Rectangle {
                anchors.fill: parent
                color: "#f0f0f0"
                radius: 5

                Column {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 10

                    Text {
                        text: "TTS 模型"
                        font.bold: true
                        font.pixelSize: 16
                    }

                    Item {
                        width: parent.width
                        height: parent.height

                        ListView {
                            clip: true
                            model: ttsModelList
                            height: 100
                            delegate: modelDelegate

                            onContentHeightChanged: {
                                console.log("TTS 列表项数量:", count);
                            }
                        }
                    }
                }
            }
        }
    }
}