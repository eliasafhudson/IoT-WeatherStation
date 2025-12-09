# Aquí definimos datos importantes como el ID del dispositivo,
# la red WiFi, el servidor MQTT y los temas de comunicación.

DEVICE_ID = "ws-esp32-001"   # Identificador único del dispositivo.

# Tema (canal) para enviar comandos al dispositivo.
TOPIC_CMD  = f"iot/weather/{DEVICE_ID}/cmd"

# Datos de la red WiFi a la que se conectará el dispositivo.
WIFI_SSID = "Wokwi-GUEST"    # Nombre de la red WiFi.
WIFI_PASSWORD = ""           # Contraseña de la red (aquí está vacía porque Wokwi no requiere clave).

# Datos del servidor MQTT.
MQTT_BROKER = "broker.emqx.io"   # Dirección del servidor MQTT.
MQTT_PORT = 1883                 # Puerto de conexión (1883 es el estándar para MQTT sin seguridad).

# Temas (canales) de comunicación MQTT.
TOPIC_TELE = f"iot/weather/{DEVICE_ID}/telemetry"   # Donde el dispositivo envía datos de sensores.
TOPIC_CMD  = f"iot/weather/{DEVICE_ID}/cmd"         # Donde se envían comandos al dispositivo.
TOPIC_EVT  = f"iot/weather/{DEVICE_ID}/event"       # Donde el dispositivo envía eventos (ejemplo: confirmaciones).

# Intervalo de tiempo entre envíos de telemetría (datos de sensores).
TELE_INTERVAL_SEC = 10   # Cada 10 segundos se envían datos.
