import network, time

def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(ssid, password)
        for _ in range(60):
            if wlan.isconnected():
                return
            time.sleep(0.2)
    if not wlan.isconnected():
        raise RuntimeError("No se pudo conectar a WiFi")
