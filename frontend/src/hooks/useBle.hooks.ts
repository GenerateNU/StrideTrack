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

const RECONNECT_INTERVAL_MS = 1000;
const RECONNECT_MAX_ATTEMPTS = 30;

export function useBle() {
  const [bleIsAvailable, setBleIsAvailable] = useState(false);
  const [bleIsConnected, setBleIsConnected] = useState(false);
  const [bleIsScanning, setBleIsScanning] = useState(false);
  const [bleIsReconnecting, setBleIsReconnecting] = useState(false);

  const bufferRef = useRef<BleForceRow[]>([]);
  const startIndexRef = useRef<number | null>(null);

  // When true, disconnect was intentional — skip auto-reconnect.
  const intentionalDisconnectRef = useRef(false);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

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

  // ── Reconnect helpers ─────────────────────────────────────────

  const cancelReconnect = useCallback(() => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
    setBleIsReconnecting(false);
  }, []);

  const webSubscribeToNotifications = useCallback(
    async (device: BluetoothDevice) => {
      const server = await device.gatt!.connect();
      console.log("[BLE-web] GATT reconnected:", server.connected);

      const service = await server.getPrimaryService(FORCE_PLATE_SERVICE_UUID);
      const characteristic = await service.getCharacteristic(
        FORCE_PLATE_CHARACTERISTIC_UUID
      );
      webCharRef.current = characteristic;

      const onValue = (event: Event) => {
        const char = event.target as BluetoothRemoteGATTCharacteristic;
        if (char.value) {
          bufferRef.current.push(parseNotification(char.value));
        }
      };
      webValueListenerRef.current = onValue;
      characteristic.addEventListener("characteristicvaluechanged", onValue);

      await characteristic.startNotifications();
      console.log("[BLE-web] notifications re-started OK");
    },
    []
  );

  const attemptWebReconnect = useCallback(
    (device: BluetoothDevice, attempt: number) => {
      if (intentionalDisconnectRef.current) return;
      if (attempt > RECONNECT_MAX_ATTEMPTS) {
        console.log("[BLE-web] max reconnect attempts reached");
        setBleIsReconnecting(false);
        return;
      }

      setBleIsReconnecting(true);
      console.log(
        `[BLE-web] reconnect attempt ${attempt}/${RECONNECT_MAX_ATTEMPTS}`
      );

      reconnectTimerRef.current = setTimeout(async () => {
        try {
          await webSubscribeToNotifications(device);
          setBleIsConnected(true);
          setBleIsReconnecting(false);
          console.log("[BLE-web] reconnected successfully");
        } catch {
          attemptWebReconnect(device, attempt + 1);
        }
      }, RECONNECT_INTERVAL_MS);
    },
    [webSubscribeToNotifications]
  );

  const attemptNativeReconnect = useCallback(
    (deviceId: string, attempt: number) => {
      if (intentionalDisconnectRef.current) return;
      if (attempt > RECONNECT_MAX_ATTEMPTS) {
        console.log("[BLE-native] max reconnect attempts reached");
        setBleIsReconnecting(false);
        return;
      }

      setBleIsReconnecting(true);
      console.log(
        `[BLE-native] reconnect attempt ${attempt}/${RECONNECT_MAX_ATTEMPTS}`
      );

      reconnectTimerRef.current = setTimeout(async () => {
        try {
          await BleClient.connect(deviceId, () => {
            console.log("[BLE-native] disconnected during reconnect session");
            setBleIsConnected(false);
            if (!intentionalDisconnectRef.current) {
              attemptNativeReconnect(deviceId, 1);
            }
          });
          await BleClient.startNotifications(
            deviceId,
            FORCE_PLATE_SERVICE_UUID,
            FORCE_PLATE_CHARACTERISTIC_UUID,
            (value: DataView) => {
              bufferRef.current.push(parseNotification(value));
            }
          );
          setBleIsConnected(true);
          setBleIsReconnecting(false);
          console.log("[BLE-native] reconnected successfully");
        } catch {
          attemptNativeReconnect(deviceId, attempt + 1);
        }
      }, RECONNECT_INTERVAL_MS);
    },
    []
  );

  // ── Web Bluetooth path ───────────────────────────────────────

  const webConnect = useCallback(async () => {
    console.log("[BLE-web] requestDevice...");
    const device = await navigator.bluetooth.requestDevice({
      filters: [{ services: [FORCE_PLATE_SERVICE_UUID] }],
    });
    console.log("[BLE-web] device selected:", device.name, device.id);

    webDeviceRef.current = device;
    intentionalDisconnectRef.current = false;

    const onDisconnect = () => {
      console.log("[BLE-web] GATT server disconnected");
      setBleIsConnected(false);
      if (!intentionalDisconnectRef.current && webDeviceRef.current) {
        attemptWebReconnect(webDeviceRef.current, 1);
      }
    };
    webDisconnectListenerRef.current = onDisconnect;
    device.addEventListener("gattserverdisconnected", onDisconnect);

    console.log("[BLE-web] connecting to GATT server...");
    await webSubscribeToNotifications(device);
    console.log("[BLE-web] connected and subscribed");

    setBleIsConnected(true);
  }, [attemptWebReconnect, webSubscribeToNotifications]);

  const webDisconnect = useCallback(async () => {
    intentionalDisconnectRef.current = true;
    cancelReconnect();
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
  }, [cancelReconnect]);

  // ── Native (Capacitor) path ──────────────────────────────────

  const nativeConnect = useCallback(async () => {
    console.log("[BLE-native] initializing...");
    intentionalDisconnectRef.current = false;
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
        setBleIsConnected(false);
        if (
          !intentionalDisconnectRef.current &&
          deviceIdRef.current === device.deviceId
        ) {
          attemptNativeReconnect(device.deviceId, 1);
        }
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
  }, [attemptNativeReconnect]);

  const nativeDisconnect = useCallback(async () => {
    intentionalDisconnectRef.current = true;
    cancelReconnect();
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
  }, [cancelReconnect]);

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
    bleIsReconnecting,
    bleConnect,
    bleDisconnect,
    bleDataBuffer,
    bleMarkStart,
    bleRunBuffer,
    bleClearBuffer,
  };
}
