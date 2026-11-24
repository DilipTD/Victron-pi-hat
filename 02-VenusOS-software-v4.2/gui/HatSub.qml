import QtQuick 1.1

// Subsystem health row (classic GUI): coloured dot + reason text
MbItem {
	id: root
	property string label
	property string basePath
	property VBusItem lvl: VBusItem { bind: root.basePath }
	property VBusItem why: VBusItem { bind: root.basePath + "/Text" }
	height: 35
	MbTextDescription {
		anchors { left: parent.left; leftMargin: 10; verticalCenter: parent.verticalCenter }
		text: root.label
	}
	Rectangle {
		x: 250; width: 14; height: 14; radius: 7
		anchors.verticalCenter: parent.verticalCenter
		color: !root.lvl.valid || root.lvl.value < 0 ? "#808080" : root.lvl.value === 2 ? "#e5484d" : root.lvl.value === 1 ? "#f5a623" : "#30a46c"
	}
	Text {
		anchors { left: parent.left; leftMargin: 275; right: parent.right; rightMargin: 10; verticalCenter: parent.verticalCenter }
		font.pixelSize: 15; elide: Text.ElideRight; color: "#ffffff"
		text: root.why.valid ? root.why.value : "no data"
	}
}
