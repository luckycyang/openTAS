import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

RowLayout {
    id: root
    
    required property string display
    required property string input
    property var validator
    
    Text {
        text: parent.display
        Layout.fillWidth: true
    }

    TextField {
        text: parent.input
        Layout.fillWidth: true
        Layout.fillHeight: true
        validator: parent.validator ? parent.validator : null

        onTextChanged: root.modified(text)
    }

    // Notify parent
    signal modified(str: string)
}
