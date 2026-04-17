import CoreBluetooth
import Foundation

class Delegate: NSObject, CBPeripheralManagerDelegate {
    func peripheralManagerDidUpdateState(_ peripheral: CBPeripheralManager) {
        guard peripheral.state == .poweredOn else {
            print("Bluetooth state: \(peripheral.state.rawValue)")
            return
        }
        print("Powered on — adding service...")
        let characteristic = CBMutableCharacteristic(
            type: CBUUID(string: "2A37"),
            properties: .notify,
            value: nil,
            permissions: .readable
        )
        let service = CBMutableService(type: CBUUID(string: "180D"), primary: true)
        service.characteristics = [characteristic]
        peripheral.add(service)
    }

    func peripheralManager(_ peripheral: CBPeripheralManager, didAdd service: CBService, error: (any Error)?) {
        if let error = error {
            print("Error adding service: \(error)")
            return
        }
        print("Service added — advertising...")
        peripheral.startAdvertising([
            CBAdvertisementDataLocalNameKey: "StrideTrack Sensor",
            CBAdvertisementDataServiceUUIDsKey: [CBUUID(string: "180D")]
        ])
    }

    func peripheralManagerDidStartAdvertising(_ peripheral: CBPeripheralManager, error: (any Error)?) {
        if let error = error {
            print("Error advertising: \(error)")
            return
        }
        print("Advertising — waiting for subscription...")
    }

    func peripheralManager(_ peripheral: CBPeripheralManager, central: CBCentral, didSubscribeTo characteristic: CBCharacteristic) {
        print(">>> SUBSCRIBED: \(central.identifier)")
    }

    func peripheralManager(_ peripheral: CBPeripheralManager, central: CBCentral, didUnsubscribeFrom characteristic: CBCharacteristic) {
        print(">>> UNSUBSCRIBED: \(central.identifier)")
    }

    func peripheralManager(_ peripheral: CBPeripheralManager, didReceiveRead request: CBATTRequest) {
        print(">>> READ REQUEST: \(request.characteristic.uuid)")
    }
}

let delegate = Delegate()
let manager = CBPeripheralManager(delegate: delegate, queue: nil)

print("Running... (Ctrl+C to stop)")
RunLoop.current.run()
