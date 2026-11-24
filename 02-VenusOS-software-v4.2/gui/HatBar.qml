import QtQuick 1.1

// Bar gauge row for the classic GUI (colours fixed; thresholds optional)
MbItem {
	id: root
	property string label
	property string bindPath
	property real from: 0
	property real to: 1
	property real lowCrit: -1e9
	property real lowWarn: -1e9
	property real highWarn: 1e9
	property real highCrit: 1e9
	property string unit: ""
	property int decimals: 2
	property VBusItem it: VBusItem { bind: root.bindPath }
	property bool ok: it.valid
	property real v: it.valid ? it.value : 0
	property int level: !ok ? -1 : (v <= lowCrit || v >= highCrit) ? 2 : (v <= lowWarn || v >= highWarn) ? 1 : 0
	height: 35
	MbTextDescription {
		anchors { left: parent.left; leftMargin: 10; verticalCenter: parent.verticalCenter }
		text: root.label
	}
	Rectangle {
		id: track
		x: 270; width: 190; height: 8; radius: 4
		anchors.verticalCenter: parent.verticalCenter
		color: "#404040"
		Rectangle {
			height: parent.height; radius: 4
			width: root.ok ? parent.width * Math.max(0, Math.min(1, (root.v - root.from) / (root.to - root.from))) : 0
			color: root.level === 2 ? "#e5484d" : root.level === 1 ? "#f5a623" : "#30a46c"
		}
	}
	Text {
		anchors { right: parent.right; rightMargin: 10; verticalCenter: parent.verticalCenter }
		font.pixelSize: 16
		color: root.level === 2 ? "#e5484d" : root.level === 1 ? "#f5a623" : "#ffffff"
		text: root.ok ? root.v.toFixed(root.decimals) + " " + root.unit : "--"
	}
}
