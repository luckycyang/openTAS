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
        anchors.fill: parent
        model: logModel
        delegate: Text {
            text: roleText
            padding: 8
            width: parent.width
        }
    }

    Timer {
        id: refreshTimer
        interval: 5000 // 每 5 秒刷新一次
        repeat: true
        onTriggered: loadLogs()
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
        refreshTimer.start()
    }
}