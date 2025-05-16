import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import bridge.models 1 

Rectangle {
    anchors.fill: parent

    ListModel {
        id: modelList
    }

    ModelsBridge {
        id: modelsBridge
    }

    Component.onCompleted: {
        var names = modelsBridge.getAllModels();
        for (var i = 0; i < names.length; i++) {
            modelList.append({ "name": names[i] });
        }
    }

    Column {
        spacing: 20

        Text {
            text: "本地模型管理"
            font.bold: true
            font.pixelSize: 20
        }

        Row {
            spacing: 20

            Text {
                text: "模型名称"
                width: 100
            }
            Text {
                text: "状态"
                width: 80
            }
            Text {
                text: "操作"
            }
        }

        ListView {
            clip: true
            model: modelList
            delegate: Row {
                spacing: 20

                Text {
                    text: "• " + model.name
                    width: 100
                }

                Text {
                    id: statusText
                    text: "检查中..."
                    width: 80

                    function updateStatus() {
                        var status = modelsBridge.getContainerStatus(model.name)
                        statusText.text = status
                    }

                    Component.onCompleted: updateStatus()
                }

                Row {
                    spacing: 10

                    Button {
                        text: "启动"
                        onClicked: {
                            modelsBridge.startContainer(model.name)
                            statusText.updateStatus()
                        }
                    }

                    Button {
                        text: "停止"
                        onClicked: {
                            modelsBridge.stopContainer(model.name)
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
    }
}