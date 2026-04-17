# pip install pyobjc-framework-CoreBluetooth pyobjc-framework-libdispatch
"""Mock BLE peripheral that simulates a StrideTrack insole sensor.

Uses CoreBluetooth via pyobjc directly (instead of bless) for reliable
advertising on macOS. All setup is callback-driven on the main run loop
so delegate methods fire reliably.

Reads a CSV file and streams rows continuously as BLE notifications at
~100Hz. Loops back to the start of the CSV when all rows have been sent,
streaming until the central disconnects.

Supports two CSV formats:
  - Force plate: Time, Force_Foot1, Force_Foot2
  - Sensor log:  timestamp_ms, sensor_id, value
"""

from __future__ import annotations

import argparse
import csv
import logging
import struct
import sys
import time
import threading

import objc
from CoreBluetooth import (
    CBAdvertisementDataLocalNameKey,
    CBAdvertisementDataServiceUUIDsKey,
    CBATTErrorAttributeNotFound,
    CBATTErrorSuccess,
    CBAttributePermissionsReadable,
    CBCharacteristicPropertyNotify,
    CBCharacteristicPropertyRead,
    CBMutableCharacteristic,
    CBMutableService,
    CBPeripheralManager,
)
from Foundation import CBUUID, NSData, NSObject
from PyObjCTools import AppHelper

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

SERVICE_UUID = "0000180d-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

NOTIFICATION_INTERVAL_S = 0.01  # 100 Hz


# ── CSV loading ────────────────────────────────────────────────


def load_csv(path: str) -> list[tuple[float, float, float]]:
    """Load a CSV and return rows as (time, force_foot1, force_foot2) tuples.

    Detects format automatically:
      - Columns Time, Force_Foot1, Force_Foot2 -> use directly
      - Columns timestamp_ms, sensor_id, value -> pivot sensor pairs into rows
    """
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []

        if "Time" in headers and "Force_Foot1" in headers and "Force_Foot2" in headers:
            return _load_force_plate_format(reader)
        elif (
            "timestamp_ms" in headers
            and "sensor_id" in headers
            and "value" in headers
        ):
            return _load_sensor_log_format(reader)
        else:
            logger.error(
                "Unrecognized CSV format. Expected columns: "
                "(Time, Force_Foot1, Force_Foot2) or "
                "(timestamp_ms, sensor_id, value)"
            )
            sys.exit(1)


def _load_force_plate_format(
    reader: csv.DictReader,
) -> list[tuple[float, float, float]]:
    """Parse rows with Time, Force_Foot1, Force_Foot2 columns."""
    rows: list[tuple[float, float, float]] = []
    for row in reader:
        rows.append((
            float(row["Time"]),
            float(row["Force_Foot1"]),
            float(row["Force_Foot2"]),
        ))
    return rows


def _load_sensor_log_format(
    reader: csv.DictReader,
) -> list[tuple[float, float, float]]:
    """Pivot sensor log rows (timestamp_ms, sensor_id, value) into force plate rows.

    Groups by timestamp_ms. Assumes sensor_id 1 = foot1, sensor_id 2 = foot2.
    """
    by_time: dict[float, dict[int, float]] = {}
    for row in reader:
        ts = float(row["timestamp_ms"])
        sid = int(row["sensor_id"])
        val = float(row["value"])
        if ts not in by_time:
            by_time[ts] = {}
        by_time[ts][sid] = val

    rows: list[tuple[float, float, float]] = []
    for ts in sorted(by_time):
        sensors = by_time[ts]
        foot1 = sensors.get(1, 0.0)
        foot2 = sensors.get(2, 0.0)
        rows.append((ts, foot1, foot2))
    return rows


def pack_notification(time_val: float, foot1: float, foot2: float) -> bytes:
    """Pack 3 floats as little-endian bytes (12 bytes total)."""
    return struct.pack("<fff", time_val, foot1, foot2)


# ── CoreBluetooth delegate ──────────────────────────────────────


class PeripheralDelegate(NSObject):
    """CBPeripheralManagerDelegate — fully callback-driven on the main queue."""

    def init(self):
        self = objc.super(PeripheralDelegate, self).init()
        if self is None:
            return None
        self._subscribed = threading.Event()
        self._characteristic = None
        self._manager = None
        self._rows = []
        return self

    # -- State changes → build service --

    def peripheralManagerDidUpdateState_(self, peripheral):
        state = peripheral.state()
        if state == 5:  # CBManagerStatePoweredOn
            logger.info("Bluetooth powered on — adding service...")
            self._build_and_add_service(peripheral)
        else:
            logger.warning("Bluetooth state changed: %d (need 5/poweredOn)", state)

    @objc.python_method
    def _build_and_add_service(self, peripheral):
        char_uuid = CBUUID.UUIDWithString_(CHARACTERISTIC_UUID)
        characteristic = (
            CBMutableCharacteristic.alloc()
            .initWithType_properties_value_permissions_(
                char_uuid,
                CBCharacteristicPropertyNotify | CBCharacteristicPropertyRead,
                None,
                CBAttributePermissionsReadable,
            )
        )
        self._characteristic = characteristic

        service_uuid = CBUUID.UUIDWithString_(SERVICE_UUID)
        service = CBMutableService.alloc().initWithType_primary_(service_uuid, True)
        service.setCharacteristics_([characteristic])

        peripheral.addService_(service)

    # -- Service added → start advertising --

    def peripheralManager_didAddService_error_(self, peripheral, service, error):
        if error:
            logger.error("Failed to add service: %s", error)
            return
        logger.info("Service added — starting advertising...")
        service_uuid = CBUUID.UUIDWithString_(SERVICE_UUID)
        peripheral.startAdvertising_(
            {
                CBAdvertisementDataLocalNameKey: "StrideTrack Sensor",
                CBAdvertisementDataServiceUUIDsKey: [service_uuid],
            }
        )

    # -- Advertising started --

    def peripheralManagerDidStartAdvertising_error_(self, peripheral, error):
        if error:
            logger.error("Failed to start advertising: %s", error)
            return
        logger.info(
            "Advertising as 'StrideTrack Sensor' — waiting for subscription..."
        )

    # -- Subscription --

    def peripheralManager_central_didSubscribeToCharacteristic_(
        self, peripheral, central, characteristic
    ):
        logger.info("Central subscribed: %s", central.identifier())
        self._subscribed.set()

    def peripheralManager_central_didUnsubscribeFromCharacteristic_(
        self, peripheral, central, characteristic
    ):
        logger.info("Central unsubscribed: %s", central.identifier())
        self._subscribed.clear()

    # -- Read requests --

    def peripheralManager_didReceiveReadRequest_(self, peripheral, request):
        logger.info("Read request for %s", request.characteristic().UUID())
        char_uuid = CBUUID.UUIDWithString_(CHARACTERISTIC_UUID)
        if request.characteristic().UUID().isEqual_(char_uuid):
            request.setValue_(NSData.data())
            peripheral.respondToRequest_withResult_(request, CBATTErrorSuccess)
        else:
            peripheral.respondToRequest_withResult_(request, CBATTErrorAttributeNotFound)

    # -- Write requests --

    def peripheralManager_didReceiveWriteRequests_(self, peripheral, requests):
        logger.info("Received %d write request(s)", requests.count())
        for i in range(requests.count()):
            req = requests.objectAtIndex_(i)
            logger.info("  Write to %s: %s", req.characteristic().UUID(), req.value())
        peripheral.respondToRequest_withResult_(
            requests.objectAtIndex_(0), CBATTErrorSuccess
        )


# ── Notification streaming (runs on a background thread) ────────


def _stream_notifications(delegate):
    """Stream CSV rows continuously as BLE notifications at ~100Hz.

    Loops back to the start of the CSV when all rows have been sent,
    so the stream runs until the central disconnects.
    """
    rows = delegate._rows
    manager = delegate._manager
    characteristic = delegate._characteristic

    row_index = 0
    notifications_sent = 0

    while delegate._subscribed.is_set():
        time_val, foot1, foot2 = rows[row_index]
        payload = pack_notification(time_val, foot1, foot2)
        ns_data = NSData.dataWithBytes_length_(payload, len(payload))

        did_send = manager.updateValue_forCharacteristic_onSubscribedCentrals_(
            ns_data, characteristic, None
        )
        if not did_send:
            time.sleep(NOTIFICATION_INTERVAL_S)
            continue

        row_index = (row_index + 1) % len(rows)
        notifications_sent += 1

        if notifications_sent % 100 == 0:
            logger.info("Sent %d notifications (row %d/%d)", notifications_sent, row_index, len(rows))

        time.sleep(NOTIFICATION_INTERVAL_S)

    logger.info(
        "Central unsubscribed — stopped after %d notifications", notifications_sent
    )


# ── Main entry point ────────────────────────────────────────────


def run_peripheral(csv_path: str) -> None:
    """Run the mock BLE peripheral on the main run loop."""
    rows = load_csv(csv_path)
    if not rows:
        logger.error("CSV file is empty or has no valid rows")
        sys.exit(1)

    logger.info("Loaded %d rows from %s", len(rows), csv_path)

    delegate = PeripheralDelegate.alloc().init()
    delegate._rows = rows

    # Use None (main queue) — callbacks fire on the main run loop,
    # so no GIL contention with a separate dispatch queue thread.
    manager = CBPeripheralManager.alloc().initWithDelegate_queue_(delegate, None)
    delegate._manager = manager

    # Background thread waits for subscription, then streams data.
    def _wait_and_stream():
        delegate._subscribed.wait()
        logger.info("Starting notification stream...")
        _stream_notifications(delegate)

    threading.Thread(target=_wait_and_stream, daemon=True).start()

    # The main run loop processes all CoreBluetooth callbacks.
    # Setup is driven by the delegate: poweredOn → addService → advertise.
    AppHelper.runConsoleEventLoop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Mock BLE peripheral simulating a StrideTrack force plate sensor"
    )
    parser.add_argument(
        "csv_path",
        help="Path to CSV file (Time/Force_Foot1/Force_Foot2 or timestamp_ms/sensor_id/value)",
    )
    args = parser.parse_args()

    run_peripheral(args.csv_path)
