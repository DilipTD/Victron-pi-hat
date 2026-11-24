import QtQuick 1.1

// Victron HAT status (board v28.0: no ADC diagnostics) - overall health, ports/VE.Can, Venus OS system
MbPage {
	id: root
	title: qsTr("Victron HAT status")
	model: VisualItemModel {
		HatScore {}
		HatSub { label: qsTr("Ports and VE.Can"); basePath: "com.victronenergy.vichat/Health/Comms" }
		HatSub { label: qsTr("Venus OS system"); basePath: "com.victronenergy.vichat/Health/System" }
		MbItemValue {
			description: qsTr("Board config")
			item.bind: "com.victronenergy.vichat/Config"
		}
		HatBar { label: qsTr("CPU load"); bindPath: "com.victronenergy.vichat/System/CpuLoadPct"; from: 0; to: 100; highWarn: 85; highCrit: 95; unit: "%"; decimals: 0 }
		HatBar { label: qsTr("CPU temperature"); bindPath: "com.victronenergy.vichat/System/CpuTempC"; from: 20; to: 100; highWarn: 70; highCrit: 80; unit: "C"; decimals: 0 }
		HatBar { label: qsTr("RAM used"); bindPath: "com.victronenergy.vichat/System/RamPct"; from: 0; to: 100; highWarn: 85; highCrit: 95; unit: "%"; decimals: 0 }
		HatBar { label: qsTr("/data used"); bindPath: "com.victronenergy.vichat/System/DataPct"; from: 0; to: 100; highWarn: 85; highCrit: 95; unit: "%"; decimals: 0 }
		MbSubMenu { description: qsTr("Venus OS system: CPU, RAM, storage"); subpage: Component { PageVictronHatSystem {} } }
		MbSubMenu { description: qsTr("Ports, VE.Can, outputs, inputs"); subpage: Component { PageVictronHatAll {} } }
	}
}
