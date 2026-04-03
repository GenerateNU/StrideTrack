# pip install pyobjc-framework-CoreBluetooth pyobjc-framework-libdispatch
"""Mock BLE peripheral that simulates a StrideTrack insole sensor.

Uses CoreBluetooth via pyobjc directly (instead of bless) for reliable
advertising on macOS. Runs on the CFRunLoop, which CBPeripheralManager
requires on macOS.

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
    CBAttributePermissionsReadable,
    CBCharacteristicPropertyNotify,
    CBMutableCharacteristic,
    CBMutableService,
    CBPeripheralManager,
)
from Foundation import CBUUID, NSData, NSObject
from dispatch import dispatch_queue_create, DISPATCH_QUEUE_SERIAL
from PyObjCTools import AppHelper

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

SERVICE_UUID = "0000180d-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

NOTIFICATION_INTERVAL_S = 0.01  # 100 Hz


# ── CSV loading (unchanged) ─────────────────────────────────────


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
    """CBPeripheralManagerDelegate that manages the GATT service lifecycle."""

    def init(self):
        self = objc.super(PeripheralDelegate, self).init()
        if self is None:
            return None
        self._powered_on = threading.Event()
        self._subscribed = threading.Event()
        self._service_added = threading.Event()
        self._characteristic = None
        self._manager = None
        self._rows = []
        return self

    # -- State changes --

    def peripheralManagerDidUpdateState_(self, peripheral):
        state = peripheral.state()
        # CBManagerStatePoweredOn == 5
        if state == 5:
            logger.info("Bluetooth powered on")
            self._powered_on.set()
        else:
            logger.warning("Bluetooth state changed: %d (need 5/poweredOn)", state)

    # -- Service added --

    def peripheralManager_didAddService_error_(self, peripheral, service, error):
        if error:
            logger.error("Failed to add service: %s", error)
            return
        logger.info("Service added successfully")
        self._service_added.set()

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

        # Send notification — returns False when the transmit queue is full
        did_send = manager.updateValue_forCharacteristic_onSubscribedCentrals_(
            ns_data, characteristic, None
        )
        if not did_send:
            # Back off briefly and retry the same row
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
    """Run the mock BLE peripheral on the CFRunLoop."""
    rows = load_csv(csv_path)
    if not rows:
        logger.error("CSV file is empty or has no valid rows")
        sys.exit(1)

    logger.info("Loaded %d rows from %s", len(rows), csv_path)

    delegate = PeripheralDelegate.alloc().init()
    delegate._rows = rows

    # Use a serial dispatch queue so CoreBluetooth callbacks are
    # delivered off the main thread but in order.
    queue = dispatch_queue_create(b"com.stridetrack.ble", DISPATCH_QUEUE_SERIAL)
    manager = CBPeripheralManager.alloc().initWithDelegate_queue_(delegate, queue)
    delegate._manager = manager

    # Wait for Bluetooth to power on
    logger.info("Waiting for Bluetooth to power on...")
    delegate._powered_on.wait()

    # Build the characteristic
    char_uuid = CBUUID.UUIDWithString_(CHARACTERISTIC_UUID)
    characteristic = (
        CBMutableCharacteristic.alloc()
        .initWithType_properties_value_permissions_(
            char_uuid,
            CBCharacteristicPropertyNotify,
            None,
            CBAttributePermissionsReadable,
        )
    )
    delegate._characteristic = characteristic

    # Build the service
    service_uuid = CBUUID.UUIDWithString_(SERVICE_UUID)
    service = CBMutableService.alloc().initWithType_primary_(service_uuid, True)
    service.setCharacteristics_([characteristic])

    manager.addService_(service)
    delegate._service_added.wait()

    # Start advertising
    manager.startAdvertising_(
        {
            CBAdvertisementDataLocalNameKey: "StrideTrack Sensor",
            CBAdvertisementDataServiceUUIDsKey: [service_uuid],
        }
    )

    # Wait for a central to subscribe, then stream from a background thread
    def _wait_and_stream():
        delegate._subscribed.wait()
        logger.info("Central subscribed — starting notifications")
        _stream_notifications(delegate)

    threading.Thread(target=_wait_and_stream, daemon=True).start()

    # Run the CFRunLoop on the main thread (required by CoreBluetooth)
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
