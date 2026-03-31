import { useState, useRef, useCallback } from "react";
import { Capacitor } from "@capacitor/core";
import { BleClient } from "@capacitor-community/bluetooth-le";

const FORCE_PLATE_SERVICE_UUID = "0000180d-0000-1000-8000-00805f9b34fb";
const FORCE_PLATE_CHARACTERISTIC_UUID = "0000180d-0000-1000-8000-00805f9b34fb";

export interface BleForceRow {
  time: number;
  force_foot1: number;
  force_foot2: number;
}

function parseNotification(value: DataView): BleForceRow {
  const time = value.getFloat32(0, true);
  const force_foot1 = value.getFloat32(4, true);
  const force_foot2 = value.getFloat32(8, true);
  return { time, force_foot1, force_foot2 };
}

export function useBle() {
  const [bleIsAvailable, setBleIsAvailable] = useState(false);
  const [bleIsConnected, setBleIsConnected] = useState(false);
  const [bleIsScanning, setBleIsScanning] = useState(false);

  const bufferRef = useRef<BleForceRow[]>([]);
  const deviceIdRef = useRef<string | null>(null);

  const checkAvailability = useCallback(async (): Promise<boolean> => {
    if (!Capacitor.isNativePlatform()) {
      setBleIsAvailable(false);
      return false;
    }
    try {
      await BleClient.initialize();
      const enabled = await BleClient.isEnabled();
      setBleIsAvailable(enabled);
      return enabled;
    } catch {
      setBleIsAvailable(false);
      return false;
    }
  }, []);

  const startListening = useCallback(async (deviceId: string) => {
    await BleClient.startNotifications(
      deviceId,
      FORCE_PLATE_SERVICE_UUID,
      FORCE_PLATE_CHARACTERISTIC_UUID,
      (value: DataView) => {
        const row = parseNotification(value);
        bufferRef.current.push(row);
      }
    );
  }, []);

  const handleDisconnect = useCallback((deviceId: string) => {
    if (deviceIdRef.current === deviceId) {
      setBleIsConnected(false);
    }
  }, []);

  const bleConnect = useCallback(async () => {
    const available = await checkAvailability();
    if (!available) {
      throw new Error("BLE is not available");
    }

    setBleIsScanning(true);
    try {
      const device = await BleClient.requestDevice({
        services: [FORCE_PLATE_SERVICE_UUID],
      });

      setBleIsScanning(false);
      deviceIdRef.current = device.deviceId;

      await BleClient.connect(device.deviceId, () =>
        handleDisconnect(device.deviceId)
      );
      setBleIsConnected(true);

      await startListening(device.deviceId);
    } catch (error) {
      setBleIsScanning(false);
      throw error;
    }
  }, [checkAvailability, handleDisconnect, startListening]);

  const bleDisconnect = useCallback(async () => {
    const deviceId = deviceIdRef.current;
    if (!deviceId) return;

    try {
      await BleClient.stopNotifications(
        deviceId,
        FORCE_PLATE_SERVICE_UUID,
        FORCE_PLATE_CHARACTERISTIC_UUID
      );
    } catch {
      // notifications may already be stopped
    }

    try {
      await BleClient.disconnect(deviceId);
    } catch {
      // device may already be disconnected
    }

    setBleIsConnected(false);
    deviceIdRef.current = null;
  }, []);

  const bleDataBuffer = useCallback((): BleForceRow[] => {
    return [...bufferRef.current];
  }, []);

  const bleClearBuffer = useCallback(() => {
    bufferRef.current = [];
  }, []);

  return {
    bleIsAvailable,
    bleIsConnected,
    bleIsScanning,
    bleConnect,
    bleDisconnect,
    bleDataBuffer,
    bleClearBuffer,
  };
}
