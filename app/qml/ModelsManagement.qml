// ModelsManagement.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import bridge.models 1

Rectangle {
    anchors.fill: parent
    color: "#ffffff"

    // 模型管理桥接实例
    ModelsBridge {
        id: modelsBridge
        onStatusChanged: function(modelType, name, status) {
            var model = (modelType === "stt" ? sttModelList : ttsModelList)
            for (var i = 0; i < model.count; i++) {
                if (model.get(i).name === name) {
                    model.setProperty(i, "status", status)
                    break
                }
            }
        }
    }

    // 动态模型委托
    Component {
        id: dynamicModelDelegate

        Row {
            spacing: 20
            height: 40
            
            Text {
                text: "• " + (name || "未知")
                width: 200
                color: "black"
                font.pixelSize: 14
            }

            Text {
                id: statusText
                text: status === "running" ? "运行中" : 
                     status === "stopped" ? "已停止" : 
                     status === "created" ? "已创建" : "未知状态"
                width: 80
                color: status === "running" ? "green" : 
                       status === "stopped" ? "red" : "gray"
            }

            Row {
                spacing: 10
                Button {
                    text: "启动"
                    enabled: status !== "running"
                    onClicked: modelsBridge.startContainer(type, name)
                }
                Button {
                    text: "停止"
                    enabled: status === "running"
                    onClicked: modelsBridge.stopContainer(type, name)
                }
                Button {
                    text: "刷新"
                    onClicked: {
                        var newStatus = modelsBridge.getContainerStatus(type, name)
                    }
                }
                Button {
                    text: "删除"
                    onClicked: {
                        modelsBridge.removeModel(type, name)
                        _refreshList(type) // 删除后刷新列表
                    }
                }
            }
        }
    }

    // 动态数据模型
    ListModel {
        id: sttModelList
    }

    ListModel {
        id: ttsModelList
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 20
        
        Text {
            text: "本地模型管理"
            font.bold: true
            font.pixelSize: 20
            Layout.leftMargin: 20
        }

        Row {
            spacing: 10
            width: parent.width
            Layout.leftMargin: 20

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
                    var type = modelTypeComboBox.model[modelTypeComboBox.currentIndex]
                    var name = modelNameInput.text
                    if (name) {
                        console.log("添加模型: " + type + " " + name)
                        modelsBridge.addModel(type, name)
                        modelNameInput.text = ""
                        _refreshList(type)
                    }
                }
            }

            Button {
                text: "刷新列表"
                onClicked: {
                    _refreshAll()
                }
            }
        }

        // STT 模型列表
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
                    ListView {
                        width: parent.width
                        height: 150
                        model: sttModelList
                        delegate: dynamicModelDelegate
                        clip: true
                    }
                }
            }
        }

        // TTS 模型列表
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
                        text: "TTS 模型"
                        font.bold: true
                        font.pixelSize: 16
                    }
                    ListView {
                        width: parent.width
                        height: 150
                        model: ttsModelList
                        delegate: dynamicModelDelegate
                        clip: true
                    }
                }
            }
        }
    }

    // 初始化加载数据
    Component.onCompleted: {
        _refreshAll()
    }

    // 刷新所有数据
    function _refreshAll() {
        _refreshList("stt")
        _refreshList("tts")
    }

    // 刷新指定类型列表
    function _refreshList(model_type) {
        var model = (model_type === "stt" ? sttModelList : ttsModelList)
        model.clear()
        
        var names = modelsBridge.getAllModelsByType(model_type)
        for (var i = 0; i < names.length; i++) {
            var name = names[i]
            var status = modelsBridge.getContainerStatus(model_type, name)
            model.append({
                "name": name,
                "type": model_type,
                "status": status
            })
        }
    }
}