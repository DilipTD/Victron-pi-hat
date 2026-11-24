import QtQuick 1.1
import "utils.js" as Utils

MbPage {
	id: root
	title: qsTr("Ports, VE.Can, outputs, inputs")
	property VBusItem fanPresent: VBusItem { bind: "com.victronenergy.vichat/Fan/Present" }
	model: VisualItemModel {
		MbItemValue {
			description: qsTr("Board config")
			item.bind: "com.victronenergy.vichat/Config"
		}
		MbItemValue {
			description: qsTr("J301 VE.Direct (ttySC0)")
			item.bind: "com.victronenergy.vichat/Port/0/Device"
		}
		MbItemValue {
			description: qsTr("J302 VE.Direct (ttySC1)")
			item.bind: "com.victronenergy.vichat/Port/1/Device"
		}
		MbItemValue {
			description: qsTr("J401 VE.Direct (ttySC2)")
			item.bind: "com.victronenergy.vichat/Port/2/Device"
		}
		MbItemValue {
			description: qsTr("J402 RS485 (ttySC3)")
			item.bind: "com.victronenergy.vichat/Port/3/Device"
		}
		MbItemValue {
			description: qsTr("J501 VE.Can state")
			item.bind: "com.victronenergy.vichat/Can/State"
		}
		MbItemValue {
			description: qsTr("J501 VE.Can errors")
			item.bind: "com.victronenergy.vichat/Can/Errors"
		}
		MbItemValue {
			description: qsTr("J501 VE.Can devices")
			item.bind: "com.victronenergy.vichat/Can/Devices"
		}
		MbItemValue {
			description: qsTr("OUT1 relay")
			item.bind: "com.victronenergy.vichat/Out/0"
		}
		MbItemValue {
			description: qsTr("OUT2 relay")
			item.bind: "com.victronenergy.vichat/Out/1"
		}
		MbItemValue {
			description: qsTr("OUT3 relay")
			item.bind: "com.victronenergy.vichat/Out/2"
		}
		MbItemValue {
			description: qsTr("OUT4 relay")
			item.bind: "com.victronenergy.vichat/Out/3"
		}
		MbItemOptions {
			description: qsTr("OUT5 fan (J603)")
			bind: "com.victronenergy.vichat/Fan/Mode"
			show: fanPresent.valid && fanPresent.value === 1
			possibleValues: [
				MbOption { description: qsTr("Off"); value: 0 },
				MbOption { description: qsTr("On"); value: 1 },
				MbOption { description: qsTr("Auto (5 V supply temperature)"); value: 2 }
			]
		}
		MbItemValue {
			description: qsTr("OUT5 fan state")
			item.bind: "com.victronenergy.vichat/Fan/State"
			show: fanPresent.valid && fanPresent.value === 1
		}
		MbItemValue {
			description: qsTr("IN1 input")
			item.bind: "com.victronenergy.vichat/In/0"
		}
		MbItemValue {
			description: qsTr("IN2 input")
			item.bind: "com.victronenergy.vichat/In/1"
		}
		MbItemValue {
			description: qsTr("IN3 input")
			item.bind: "com.victronenergy.vichat/In/2"
		}
		MbItemValue {
			description: qsTr("IN4 input")
			item.bind: "com.victronenergy.vichat/In/3"
		}
		MbSwitch {
			name: qsTr("Buzzer test")
			bind: "com.victronenergy.vichat/Buzzer/Test"
		}
	}
}
