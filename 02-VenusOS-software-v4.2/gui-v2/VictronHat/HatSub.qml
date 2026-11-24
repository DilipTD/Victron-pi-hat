import QtQuick
import Victron.GuiPlugins

// One subsystem row: coloured dot + reason text.  reads /Health/<name> from the vichat service (instance 0).
PluginListSetting {
	id: root
	property string name
	property string svc: "vichat"
	property int inst: 0
	property PluginDataItem lvl: PluginDataItem { serviceType: root.svc; deviceInstance: root.inst; path: "/Health/" + root.name }
	property PluginDataItem why: PluginDataItem { serviceType: root.svc; deviceInstance: root.inst; path: "/Health/" + root.name + "/Text" }
	Item {
		implicitWidth: 380
		implicitHeight: 28
		Rectangle {
			y: 6; width: 16; height: 16; radius: 8
			color: !root.lvl.valid || root.lvl.value < 0 ? "#808080" : root.lvl.value === 2 ? "#e5484d" : root.lvl.value === 1 ? "#f5a623" : "#30a46c"
		}
		Text {
			x: 24; width: 356; height: 28; font.pixelSize: 17; elide: Text.ElideRight; verticalAlignment: Text.AlignVCenter; color: "#c8d0d8"
			text: root.why.valid ? String(root.why.value) : "no data"
		}
	}
}
