import QtQuick
import Victron.GuiPlugins

// Bar gauge row: label on the left, coloured bar + value on the right. Colours are fixed (plugins cannot read the GUI theme).
PluginListSetting {
	id: root
	property string path
	property int inst: 0
	property string svc: "vichat"
	property real from: 0
	property real to: 1
	property real lowCrit: -1e9
	property real lowWarn: -1e9
	property real highWarn: 1e9
	property real highCrit: 1e9
	property string unit: ""
	property int decimals: 2
	readonly property real v: di.value
	readonly property bool ok: di.valid && !isNaN(v)
	readonly property int level: !ok ? -1 : (v <= lowCrit || v >= highCrit) ? 2 : (v <= lowWarn || v >= highWarn) ? 1 : 0
	property PluginDataItem di: PluginDataItem {
		serviceType: root.svc
		deviceInstance: root.inst
		path: root.path
	}
	Item {
		implicitWidth: 300
		implicitHeight: 26
		Rectangle {
			id: track
			x: 0; y: 9; width: 190; height: 8; radius: 4
			color: "#40808080"
			Rectangle {
				height: parent.height; radius: 4
				width: root.ok ? parent.width * Math.max(0, Math.min(1, (root.v - root.from) / (root.to - root.from))) : 0
				color: root.level === 2 ? "#e5484d" : root.level === 1 ? "#f5a623" : "#30a46c"
			}
		}
		Text {
			x: 200; width: 100; height: 26
			horizontalAlignment: Text.AlignRight; verticalAlignment: Text.AlignVCenter
			font.pixelSize: 18
			color: root.level === 2 ? "#e5484d" : root.level === 1 ? "#f5a623" : "#a0a8b0"
			text: root.ok ? root.v.toFixed(root.decimals) + " " + root.unit : "--"
		}
	}
}
