import { useState, useRef, useCallback, useEffect } from "react";
import { BleClient } from "@capacitor-community/bluetooth-le";
import type { BleForceRow } from "@/types/ble.types";

export type { BleForceRow };

const FORCE_PLATE_SERVICE_UUID = "0000180d-0000-1000-8000-00805f9b34fb";
const FORCE_PLATE_CHARACTERISTIC_UUID = "00002a37-0000-1000-8000-00805f9b34fb";

// True when running in a browser that supports Web Bluetooth.
// On native Capacitor (iOS/Android), WKWebView/WebView don't expose navigator.bluetooth,
// so this is false and we fall through to the BleClient (Capacitor) path.
const IS_WEB_BLUETOOTH = "bluetooth" in navigator;

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
  const startIndexRef = useRef<number | null>(null);

  // ── Native (Capacitor) refs ──────────────────────────────────
  const deviceIdRef = useRef<string | null>(null);

  // ── Web Bluetooth refs ───────────────────────────────────────
  const webDeviceRef = useRef<BluetoothDevice | null>(null);
  const webCharRef = useRef<BluetoothRemoteGATTCharacteristic | null>(null);
  const webDisconnectListenerRef = useRef<(() => void) | null>(null);
  const webValueListenerRef = useRef<((event: Event) => void) | null>(null);

  // ── Availability check ───────────────────────────────────────

  useEffect(() => {
    let cancelled = false;

    async function resolve() {
      let available = false;
      if (IS_WEB_BLUETOOTH) {
        available = true; // picker will surface unavailability at connect time
      } else {
        try {
          await BleClient.initialize();
          available = await BleClient.isEnabled();
        } catch {
          available = false;
        }
      }
      if (!cancelled) setBleIsAvailable(available);
    }

    resolve();
    return () => {
      cancelled = true;
    };
  }, []);

  // ── Web Bluetooth path ───────────────────────────────────────

  const webConnect = useCallback(async () => {
    console.log("[BLE-web] requestDevice...");
    const device = await navigator.bluetooth.requestDevice({
      filters: [{ services: [FORCE_PLATE_SERVICE_UUID] }],
    });
    console.log("[BLE-web] device selected:", device.name, device.id);

    webDeviceRef.current = device;

    const onDisconnect = () => {
      console.log("[BLE-web] GATT server disconnected");
      setBleIsConnected(false);
    };
    webDisconnectListenerRef.current = onDisconnect;
    device.addEventListener("gattserverdisconnected", onDisconnect);

    console.log("[BLE-web] connecting to GATT server...");
    const server = await device.gatt!.connect();
    console.log("[BLE-web] GATT connected:", server.connected);

    console.log("[BLE-web] getPrimaryService...");
    const service = await server.getPrimaryService(FORCE_PLATE_SERVICE_UUID);
    console.log("[BLE-web] service found");

    console.log("[BLE-web] getCharacteristic...");
    const characteristic = await service.getCharacteristic(
      FORCE_PLATE_CHARACTERISTIC_UUID
    );
    console.log("[BLE-web] characteristic properties:", {
      notify: characteristic.properties.notify,
      read: characteristic.properties.read,
      indicate: characteristic.properties.indicate,
      write: characteristic.properties.write,
    });

    webCharRef.current = characteristic;

    const onValue = (event: Event) => {
      const char = event.target as BluetoothRemoteGATTCharacteristic;
      if (char.value) {
        bufferRef.current.push(parseNotification(char.value));
      }
    };
    webValueListenerRef.current = onValue;
    characteristic.addEventListener("characteristicvaluechanged", onValue);

    console.log("[BLE-web] startNotifications...");
    await characteristic.startNotifications();
    console.log("[BLE-web] notifications started OK");

    setBleIsConnected(true);
  }, []);

  const webDisconnect = useCallback(async () => {
    if (webCharRef.current) {
      if (webValueListenerRef.current) {
        webCharRef.current.removeEventListener(
          "characteristicvaluechanged",
          webValueListenerRef.current
        );
        webValueListenerRef.current = null;
      }
      try {
        await webCharRef.current.stopNotifications();
      } catch {
        // may already be stopped
      }
      webCharRef.current = null;
    }
    if (webDeviceRef.current) {
      if (webDisconnectListenerRef.current) {
        webDeviceRef.current.removeEventListener(
          "gattserverdisconnected",
          webDisconnectListenerRef.current
        );
        webDisconnectListenerRef.current = null;
      }
      if (webDeviceRef.current.gatt?.connected) {
        webDeviceRef.current.gatt.disconnect();
      }
    }
    webDeviceRef.current = null;
    setBleIsConnected(false);
  }, []);

  // ── Native (Capacitor) path ──────────────────────────────────

  const handleNativeDisconnect = useCallback((deviceId: string) => {
    if (deviceIdRef.current === deviceId) {
      setBleIsConnected(false);
    }
  }, []);

  const nativeConnect = useCallback(async () => {
    console.log("[BLE-native] initializing...");
    try {
      await BleClient.initialize();
      const enabled = await BleClient.isEnabled();
      console.log("[BLE-native] enabled:", enabled);
      if (!enabled) throw new Error("Bluetooth is not enabled");
    } catch (e) {
      console.error("[BLE-native] init failed:", e);
      throw new Error("BLE is not available");
    }

    setBleIsScanning(true);
    try {
      console.log("[BLE-native] requestDevice...");
      const device = await BleClient.requestDevice({
        services: [FORCE_PLATE_SERVICE_UUID],
      });
      console.log(
        "[BLE-native] device selected:",
        device.deviceId,
        device.name
      );

      setBleIsScanning(false);
      deviceIdRef.current = device.deviceId;

      console.log("[BLE-native] connecting...");
      await BleClient.connect(device.deviceId, () => {
        console.log("[BLE-native] disconnected callback fired");
        handleNativeDisconnect(device.deviceId);
      });
      console.log("[BLE-native] connected");

      console.log("[BLE-native] startNotifications...");
      await BleClient.startNotifications(
        device.deviceId,
        FORCE_PLATE_SERVICE_UUID,
        FORCE_PLATE_CHARACTERISTIC_UUID,
        (value: DataView) => {
          bufferRef.current.push(parseNotification(value));
        }
      );
      console.log("[BLE-native] notifications started OK");

      setBleIsConnected(true);
    } catch (error) {
      console.error("[BLE-native] connect failed:", error);
      setBleIsScanning(false);
      throw error;
    }
  }, [handleNativeDisconnect]);

  const nativeDisconnect = useCallback(async () => {
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

  // ── Public API (routes to correct path) ─────────────────────

  const bleConnect = useCallback(async () => {
    if (IS_WEB_BLUETOOTH) return webConnect();
    return nativeConnect();
  }, [webConnect, nativeConnect]);

  const bleDisconnect = useCallback(async () => {
    if (IS_WEB_BLUETOOTH) return webDisconnect();
    return nativeDisconnect();
  }, [webDisconnect, nativeDisconnect]);

  const bleDataBuffer = useCallback((): BleForceRow[] => {
    return [...bufferRef.current];
  }, []);

  const bleMarkStart = useCallback(() => {
    startIndexRef.current = bufferRef.current.length;
  }, []);

  const bleRunBuffer = useCallback((): BleForceRow[] => {
    const start = startIndexRef.current ?? 0;
    return bufferRef.current.slice(start);
  }, []);

  const bleClearBuffer = useCallback(() => {
    bufferRef.current = [];
    startIndexRef.current = null;
  }, []);

  return {
    bleIsAvailable,
    bleIsConnected,
    bleIsScanning,
    bleConnect,
    bleDisconnect,
    bleDataBuffer,
    bleMarkStart,
    bleRunBuffer,
    bleClearBuffer,
  };
}
