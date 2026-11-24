import QtQuick
import Victron.GuiPlugins

PluginPage {
	title: "Ports and VE.Can"
	PluginGradientListView {
		PluginSettingsListHeader { text: "Serial ports" }
		PluginListText { text: "J301 VE.Direct (ttySC0)"; dataItem.serviceType: "vichat"; dataItem.deviceInstance: 0; dataItem.path: "/Port/0/Device" }
		PluginListText { text: "J302 VE.Direct (ttySC1)"; dataItem.serviceType: "vichat"; dataItem.deviceInstance: 0; dataItem.path: "/Port/1/Device" }
		PluginListText { text: "J401 VE.Direct (ttySC2)"; dataItem.serviceType: "vichat"; dataItem.deviceInstance: 0; dataItem.path: "/Port/2/Device" }
		PluginListText { text: "J402 RS485 (ttySC3)"; dataItem.serviceType: "vichat"; dataItem.deviceInstance: 0; dataItem.path: "/Port/3/Device" }
		PluginSettingsListHeader { text: "VE.Can (J501)" }
		PluginListText { text: "State"; dataItem.serviceType: "vichat"; dataItem.deviceInstance: 0; dataItem.path: "/Can/State" }
		PluginListText { text: "Errors"; dataItem.serviceType: "vichat"; dataItem.deviceInstance: 0; dataItem.path: "/Can/Errors" }
		PluginListText { text: "Devices"; dataItem.serviceType: "vichat"; dataItem.deviceInstance: 0; dataItem.path: "/Can/Devices" }
	}
}
