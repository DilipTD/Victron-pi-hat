import QtQuick
import Victron.GuiPlugins

PluginPage {
	title: "Outputs, inputs and controls"
	PluginGradientListView {
		PluginSettingsListHeader { text: "Relay outputs (Installer access)" }
		PluginListSwitch {
			text: "OUT1 relay"
			dataItem.serviceType: "vichat"
			dataItem.deviceInstance: 0
			dataItem.path: "/Out/0/State"
			writeAccessLevel: PluginAccessLevel.Installer
		}
		PluginListSwitch {
			text: "OUT2 relay"
			dataItem.serviceType: "vichat"
			dataItem.deviceInstance: 0
			dataItem.path: "/Out/1/State"
			writeAccessLevel: PluginAccessLevel.Installer
		}
		PluginListSwitch {
			text: "OUT3 relay"
			dataItem.serviceType: "vichat"
			dataItem.deviceInstance: 0
			dataItem.path: "/Out/2/State"
			writeAccessLevel: PluginAccessLevel.Installer
		}
		PluginListSwitch {
			text: "OUT4 relay"
			dataItem.serviceType: "vichat"
			dataItem.deviceInstance: 0
			dataItem.path: "/Out/3/State"
			writeAccessLevel: PluginAccessLevel.Installer
		}
		PluginSettingsListHeader { text: "Fan (OUT5, J603)" }
		PluginListRadioButtonGroup {
			text: "Fan mode"
			optionModel: [ { display: "Off", value: 0 }, { display: "On", value: 1 }, { display: "Auto (5 V supply temperature)", value: 2 } ]
			dataItem.serviceType: "vichat"
			dataItem.deviceInstance: 0
			dataItem.path: "/Fan/Mode"
			writeAccessLevel: PluginAccessLevel.Installer
		}
		PluginListText { text: "Fan state"; dataItem.serviceType: "vichat"; dataItem.deviceInstance: 0; dataItem.path: "/Fan/State" }
		PluginSettingsListHeader { text: "Digital inputs (3.3 V, active low)" }
		PluginListText { text: "IN1 input"; dataItem.serviceType: "vichat"; dataItem.deviceInstance: 0; dataItem.path: "/In/0" }
		PluginListText { text: "IN2 input"; dataItem.serviceType: "vichat"; dataItem.deviceInstance: 0; dataItem.path: "/In/1" }
		PluginListText { text: "IN3 input"; dataItem.serviceType: "vichat"; dataItem.deviceInstance: 0; dataItem.path: "/In/2" }
		PluginListText { text: "IN4 input"; dataItem.serviceType: "vichat"; dataItem.deviceInstance: 0; dataItem.path: "/In/3" }
		PluginSettingsListHeader { text: "Test" }
		PluginListSwitch {
			text: "Buzzer test"
			dataItem.serviceType: "vichat"
			dataItem.deviceInstance: 0
			dataItem.path: "/Buzzer/Test"
			writeAccessLevel: PluginAccessLevel.Installer
		}
	}
}
