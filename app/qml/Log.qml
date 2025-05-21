import QtQuick
import QtQuick.Controls

import bridge.log 1 

Rectangle {
    anchors.fill: parent

    ListModel {
        id: logModel
    }

    LogBridge { id: logBridge }
    
    ListView {
        id: listView
        anchors.fill: parent
        model: logModel
        clip: true 

        delegate: Text {
            text: roleText
            padding: 8
            wrapMode: Text.Wrap
            width: listView.width // 确保 Text 的宽度与 ListView 一致
        }

        ScrollBar.vertical: ScrollBar {
            policy: ScrollBar.AsNeeded // 自动显示/隐藏
            width: 16                   // 滚动条宽度
            anchors.right: parent.right
        }

        // 添加滚动条交互支持
        boundsBehavior: Flickable.StopAtBounds
        interactive: true
    }

    function loadLogs() {
        var lines = logBridge.read_log().split('\n')
        logModel.clear()
        for (var i = 0; i < lines.length; i++) {
            if (lines[i].trim() !== "") {
                logModel.append({ "roleText": lines[i] })
            }
        }
    }

    Component.onCompleted: {
        loadLogs()
            if (logModel.count > 0) {
            listView.contentY = listView.contentHeight
        }
    }
}