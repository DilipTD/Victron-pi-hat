import QtQuick 1.1

MbPage {
	title: qsTr("Venus OS system")
	model: VisualItemModel {
		MbItemValue { description: qsTr("Model"); item.bind: "com.victronenergy.vichat/System/Model" }
		MbItemValue { description: qsTr("Venus OS version"); item.bind: "com.victronenergy.vichat/System/Venus" }
		MbItemValue { description: qsTr("Kernel"); item.bind: "com.victronenergy.vichat/System/Kernel" }
		MbItemValue { description: qsTr("Uptime"); item.bind: "com.victronenergy.vichat/System/Uptime" }
		MbItemValue { description: qsTr("CPU cores"); item.bind: "com.victronenergy.vichat/System/CpuCores" }
		MbItemValue { description: qsTr("CPU governor"); item.bind: "com.victronenergy.vichat/System/Governor" }
		HatBar { label: qsTr("CPU speed"); bindPath: "com.victronenergy.vichat/System/CpuMHz"; from: 0; to: 2800; unit: "MHz"; decimals: 0 }
		HatBar { label: qsTr("CPU load"); bindPath: "com.victronenergy.vichat/System/CpuLoadPct"; from: 0; to: 100; unit: "%"; decimals: 0; highWarn: 85; highCrit: 95 }
		HatBar { label: qsTr("CPU temperature"); bindPath: "com.victronenergy.vichat/System/CpuTempC"; from: 20; to: 100; unit: "C"; decimals: 0; highWarn: 70; highCrit: 80 }
		HatBar { label: qsTr("RAM used"); bindPath: "com.victronenergy.vichat/System/RamPct"; from: 0; to: 100; unit: "%"; decimals: 0; highWarn: 85; highCrit: 95 }
		HatBar { label: qsTr("RAM used (MB)"); bindPath: "com.victronenergy.vichat/System/RamUsedMB"; from: 0; to: 8192; unit: "MB"; decimals: 0 }
		MbItemValue { description: qsTr("RAM total (MB)"); item.bind: "com.victronenergy.vichat/System/RamTotalMB" }
		HatBar { label: qsTr("Swap used"); bindPath: "com.victronenergy.vichat/System/SwapPct"; from: 0; to: 100; unit: "%"; decimals: 0; highWarn: 50; highCrit: 80 }
		HatBar { label: qsTr("/data used"); bindPath: "com.victronenergy.vichat/System/DataPct"; from: 0; to: 100; unit: "%"; decimals: 0; highWarn: 85; highCrit: 95 }
		HatBar { label: qsTr("Root fs used"); bindPath: "com.victronenergy.vichat/System/RootPct"; from: 0; to: 100; unit: "%"; decimals: 0; highWarn: 85; highCrit: 95 }
		MbItemValue { description: qsTr("Power / throttling"); item.bind: "com.victronenergy.vichat/System/PiVolt" }
		MbItemValue { description: qsTr("Throttled flags"); item.bind: "com.victronenergy.vichat/System/Throttled" }
	}
}
