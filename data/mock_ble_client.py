# pip install bless
"""Mock BLE peripheral that simulates a StrideTrack force plate sensor.

Reads a CSV file and streams rows as BLE notifications at ~100Hz.
Simulates a disconnect after 3 seconds of streaming, waits 20 seconds,
then reconnects and resumes from where it left off.

Supports two CSV formats:
  - Force plate: Time, Force_Foot1, Force_Foot2
  - Sensor log:  timestamp_ms, sensor_id, value
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import logging
import struct
import sys

from bless import (
    BlessGATTCharacteristic,
    BlessServer,
    GATTAttributePermissions,
    GATTCharacteristicProperties,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

SERVICE_UUID = "0000180d-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

DISCONNECT_AFTER_S = 3.0
RECONNECT_WAIT_S = 20.0
NOTIFICATION_INTERVAL_S = 0.01  # 100 Hz


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


def pack_notification(time: float, foot1: float, foot2: float) -> bytearray:
    """Pack 3 floats as little-endian bytes (12 bytes total)."""
    return bytearray(struct.pack("<fff", time, foot1, foot2))


def server_read_request(
    characteristic: BlessGATTCharacteristic,
    **kwargs,
) -> bytearray:
    """Handle read requests by returning the current characteristic value."""
    return characteristic.value or bytearray(b"")


def server_write_request(
    characteristic: BlessGATTCharacteristic,
    value: bytearray,
    **kwargs,
) -> None:
    """Handle write requests (unused but required by bless callback)."""
    characteristic.value = value


async def run_peripheral(csv_path: str) -> None:
    """Run the mock BLE peripheral."""
    rows = load_csv(csv_path)
    if not rows:
        logger.error("CSV file is empty or has no valid rows")
        sys.exit(1)

    logger.info("Loaded %d rows from %s", len(rows), csv_path)

    server = BlessServer(name="StrideTrack Sensor")
    server.read_request_func = server_read_request
    server.write_request_func = server_write_request

    await server.add_new_service(SERVICE_UUID)
    await server.add_new_characteristic(
        SERVICE_UUID,
        CHARACTERISTIC_UUID,
        GATTCharacteristicProperties.read | GATTCharacteristicProperties.notify,
        bytearray(12),
        GATTAttributePermissions.readable,
    )

    await server.start()
    logger.info("Advertising as 'StrideTrack Sensor' — waiting for connection...")

    # Wait for a central to connect
    while not await server.is_connected():
        await asyncio.sleep(0.1)
    logger.info("Central connected")

    row_index = 0
    notifications_sent = 0
    streaming_start = asyncio.get_event_loop().time()

    while row_index < len(rows):
        # Check if we should simulate a disconnect
        elapsed = asyncio.get_event_loop().time() - streaming_start
        if elapsed >= DISCONNECT_AFTER_S and notifications_sent > 0:
            logger.info(
                "Simulating disconnect after %.1fs (%d notifications sent, "
                "paused at row %d/%d)",
                elapsed,
                notifications_sent,
                row_index,
                len(rows),
            )
            await server.stop()

            logger.info("Waiting %.0fs before reconnecting...", RECONNECT_WAIT_S)
            await asyncio.sleep(RECONNECT_WAIT_S)

            # Restart advertising and wait for reconnection
            await server.start()
            logger.info("Re-advertising — waiting for reconnection...")
            while not await server.is_connected():
                await asyncio.sleep(0.1)
            logger.info(
                "Central reconnected — resuming from row %d/%d",
                row_index,
                len(rows),
            )

            # Reset so we only disconnect once
            streaming_start = float("inf")

        # Send notification
        time_val, foot1, foot2 = rows[row_index]
        payload = pack_notification(time_val, foot1, foot2)

        char = server.get_characteristic(CHARACTERISTIC_UUID)
        if char is not None:
            char.value = payload
            server.update_value(SERVICE_UUID, CHARACTERISTIC_UUID)

        row_index += 1
        notifications_sent += 1

        if notifications_sent % 100 == 0:
            logger.info("Sent %d/%d notifications", notifications_sent, len(rows))

        await asyncio.sleep(NOTIFICATION_INTERVAL_S)

    logger.info(
        "Streaming complete — sent all %d rows (%d notifications)",
        len(rows),
        notifications_sent,
    )
    await server.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Mock BLE peripheral simulating a StrideTrack force plate sensor"
    )
    parser.add_argument(
        "csv_path",
        help="Path to CSV file (Time/Force_Foot1/Force_Foot2 or timestamp_ms/sensor_id/value)",
    )
    args = parser.parse_args()

    asyncio.run(run_peripheral(args.csv_path))
