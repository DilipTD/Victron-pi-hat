import QtQuick
import Victron.GuiPlugins

// Victron Pi HAT status for GUI v2 (board v28.0: no ADC diagnostics): overall health, subsystem rows, system gauges, sub-pages
PluginPage {
	title: "Victron HAT status"

	PluginGradientListView {
		HatHealth {}
		PluginSettingsListHeader { text: "System health" }
		HatSub { text: "Ports and VE.Can"; name: "Comms" }
		HatSub { text: "Venus OS system (CPU, RAM, disk)"; name: "System" }
		PluginListText {
			text: "Board config"
			dataItem.serviceType: "vichat"
			dataItem.deviceInstance: 0
			dataItem.path: "/Config"
		}
		PluginSettingsListHeader { text: "Live gauges" }
		HatGauge { text: "CPU load"; path: "/System/CpuLoadPct"; from: 0; to: 100; highWarn: 85; highCrit: 95; unit: "%"; decimals: 0 }
		HatGauge { text: "CPU temperature"; path: "/System/CpuTempC"; from: 20; to: 100; highWarn: 70; highCrit: 80; unit: "C"; decimals: 0 }
		HatGauge { text: "RAM used"; path: "/System/RamPct"; from: 0; to: 100; highWarn: 85; highCrit: 95; unit: "%"; decimals: 0 }
		HatGauge { text: "/data used"; path: "/System/DataPct"; from: 0; to: 100; highWarn: 85; highCrit: 95; unit: "%"; decimals: 0 }
		PluginSettingsListHeader { text: "Details" }
		PluginListNavigation { text: "Venus OS system: CPU, RAM, storage"; pageUrl: Qt.resolvedUrl("VictronHatSystem.qml") }
		PluginListNavigation { text: "Ports and VE.Can"; pageUrl: Qt.resolvedUrl("VictronHatPorts.qml") }
		PluginListNavigation { text: "Outputs, inputs and controls"; pageUrl: Qt.resolvedUrl("VictronHatControls.qml") }
	}
}
