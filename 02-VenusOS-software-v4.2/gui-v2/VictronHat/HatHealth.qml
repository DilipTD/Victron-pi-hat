import QtQuick
import Victron.GuiPlugins

// Overall health: big score, colour bar, one-line summary (from /Health/* published by vichatdiag).
PluginListSetting {
	id: root
	text: "Overall health"
	property PluginDataItem score: PluginDataItem { serviceType: "vichat"; deviceInstance: 0; path: "/Health/Score" }
	property PluginDataItem lvl: PluginDataItem { serviceType: "vichat"; deviceInstance: 0; path: "/Health/Overall" }
	property PluginDataItem sum: PluginDataItem { serviceType: "vichat"; deviceInstance: 0; path: "/Health/Summary" }
	readonly property color c: !lvl.valid || lvl.value < 0 ? "#808080" : lvl.value === 2 ? "#e5484d" : lvl.value === 1 ? "#f5a623" : "#30a46c"
	Item {
		implicitWidth: 420
		implicitHeight: 64
		Text {
			x: 0; y: 0; width: 120; height: 40; font.pixelSize: 34; font.bold: true; color: root.c
			text: root.score.valid ? Math.round(root.score.value) + "%" : "--"
		}
		Text {
			x: 124; y: 0; width: 296; height: 40; font.pixelSize: 20; verticalAlignment: Text.AlignVCenter; color: root.c
			text: !root.lvl.valid || root.lvl.value < 0 ? "No data" : root.lvl.value === 2 ? "CRITICAL" : root.lvl.value === 1 ? "WARNING" : "HEALTHY"
		}
		Rectangle {
			x: 0; y: 44; width: 420; height: 8; radius: 4; color: "#40808080"
			Rectangle { height: 8; radius: 4; color: root.c; width: root.score.valid ? 420 * Math.max(0, Math.min(100, root.score.value)) / 100 : 0 }
		}
		Text {
			x: 0; y: 54; width: 420; height: 16; font.pixelSize: 13; color: "#a0a8b0"; elide: Text.ElideRight
			text: root.sum.valid ? String(root.sum.value) : ""
		}
	}
}
