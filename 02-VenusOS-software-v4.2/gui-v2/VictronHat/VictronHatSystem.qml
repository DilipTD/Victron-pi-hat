import QtQuick
import Victron.GuiPlugins

// Venus OS / Raspberry Pi system status (published by the vichat service as /System/*)
PluginPage {
	title: "Venus OS system"
	PluginGradientListView {
		PluginSettingsListHeader { text: "Device" }
		PluginListText { text: "Model"; dataItem.serviceType: "vichat"; dataItem.deviceInstance: 0; dataItem.path: "/System/Model" }
		PluginListText { text: "Venus OS version"; dataItem.serviceType: "vichat"; dataItem.deviceInstance: 0; dataItem.path: "/System/Venus" }
		PluginListText { text: "Kernel"; dataItem.serviceType: "vichat"; dataItem.deviceInstance: 0; dataItem.path: "/System/Kernel" }
		PluginListText { text: "Uptime"; dataItem.serviceType: "vichat"; dataItem.deviceInstance: 0; dataItem.path: "/System/Uptime" }
		PluginListText { text: "CPU cores"; dataItem.serviceType: "vichat"; dataItem.deviceInstance: 0; dataItem.path: "/System/CpuCores" }
		PluginListText { text: "CPU governor"; dataItem.serviceType: "vichat"; dataItem.deviceInstance: 0; dataItem.path: "/System/Governor" }
		PluginSettingsListHeader { text: "CPU" }
		HatGauge { text: "CPU speed"; svc: "vichat"; inst: 0; path: "/System/CpuMHz"; from: 0; to: 2800; unit: "MHz"; decimals: 0 }
		HatGauge { text: "CPU load"; svc: "vichat"; inst: 0; path: "/System/CpuLoadPct"; from: 0; to: 100; unit: "%"; decimals: 0; highWarn: 85; highCrit: 95 }
		HatGauge { text: "CPU temperature"; svc: "vichat"; inst: 0; path: "/System/CpuTempC"; from: 20; to: 100; unit: "C"; decimals: 0; highWarn: 70; highCrit: 80 }
		PluginSettingsListHeader { text: "Memory and storage" }
		HatGauge { text: "RAM used"; svc: "vichat"; inst: 0; path: "/System/RamPct"; from: 0; to: 100; unit: "%"; decimals: 0; highWarn: 85; highCrit: 95 }
		HatGauge { text: "RAM used (MB)"; svc: "vichat"; inst: 0; path: "/System/RamUsedMB"; from: 0; to: 8192; unit: "MB"; decimals: 0 }
		PluginListText { text: "RAM total (MB)"; dataItem.serviceType: "vichat"; dataItem.deviceInstance: 0; dataItem.path: "/System/RamTotalMB" }
		HatGauge { text: "Swap used"; svc: "vichat"; inst: 0; path: "/System/SwapPct"; from: 0; to: 100; unit: "%"; decimals: 0; highWarn: 50; highCrit: 80 }
		HatGauge { text: "/data used"; svc: "vichat"; inst: 0; path: "/System/DataPct"; from: 0; to: 100; unit: "%"; decimals: 0; highWarn: 85; highCrit: 95 }
		HatGauge { text: "Root fs used"; svc: "vichat"; inst: 0; path: "/System/RootPct"; from: 0; to: 100; unit: "%"; decimals: 0; highWarn: 85; highCrit: 95 }
		PluginSettingsListHeader { text: "Pi power" }
		PluginListText { text: "Power / throttling"; dataItem.serviceType: "vichat"; dataItem.deviceInstance: 0; dataItem.path: "/System/PiVolt" }
		PluginListText { text: "Throttled flags"; dataItem.serviceType: "vichat"; dataItem.deviceInstance: 0; dataItem.path: "/System/Throttled" }
	}
}
