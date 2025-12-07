DEVICE_ID = "ws-esp32-001"
TOPIC_CMD  = f"iot/weather/{DEVICE_ID}/cmd"

WIFI_SSID = "Wokwi-GUEST"
WIFI_PASSWORD = ""

MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883

TOPIC_TELE = f"iot/weather/{DEVICE_ID}/telemetry"
TOPIC_CMD  = f"iot/weather/{DEVICE_ID}/cmd"
TOPIC_EVT  = f"iot/weather/{DEVICE_ID}/event"

TELE_INTERVAL_SEC = 10
