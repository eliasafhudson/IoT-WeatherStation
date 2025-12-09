print("Hello, ESP32!")   # Mensaje inicial para confirmar que el programa arrancó.

import time
import ujson   # Librería para manejar datos en formato JSON (texto estructurado).
from config import *   # Importamos configuraciones (WiFi, MQTT, etc.).
from wifi_mgr import connect_wifi   # Función para conectarse a WiFi.
from mqtt_mgr import MqttManager    # Clase para manejar conexión MQTT.
from sensors import Sensors         # Clase para leer sensores.
from actuators import Actuators     # Clase para manejar LED, buzzer y pantalla OLED.

print("BOOT: iniciando device...")

# Creamos objetos para sensores y actuadores.
sensors = Sensors()
acts = Actuators()

status = "BOOT"   # Estado inicial del dispositivo.
last_pub = 0      # Última vez que se publicó telemetría.


# Función para interpretar comandos recibidos (ejemplo: "LED=1").
def parse_command_string(s: str):
    s = (s or "").strip()
    if not s or "=" not in s:
        return None, None
    k, v = s.split("=", 1)
    return k.strip().upper(), v.strip()


# Función que se ejecuta cuando llega un mensaje MQTT.
def on_msg(topic, msg):
    global status
    print("MQTT MSG topic:", topic, "raw:", msg)

    try:
        payload = ujson.loads(msg)   # Intentamos leer el mensaje como JSON.
        cmd_str = payload.get("value", "")
    except Exception as e:
        print("JSON parse fail:", e)
        # Si no es JSON válido, lo tratamos como texto normal.
        cmd_str = msg.decode() if hasattr(msg, "decode") else str(msg)

    print("CMD_STR:", cmd_str)

    # Interpretamos el comando recibido.
    k, v = parse_command_string(cmd_str)
    print("PARSED:", k, v)

    # Si el comando es para el LED.
    if k == "LED":
        acts.set_led(v == "1")   # Encendemos o apagamos el LED.
        status = f"LED={v}"
        print("LED ejecutado:", v)
        # Reportamos el evento al servidor MQTT.
        mqtt.publish(TOPIC_EVT, {"type": "EVENT", "cmd": "LED", "val": v})

    # Si el comando es para el buzzer.
    elif k == "BEEP":
        acts.beep(ms=int(v))   # Hacemos sonar el buzzer por el tiempo indicado.
        status = f"BEEP={v}"
        print("BEEP ejecutado:", v)
        # Reportamos el evento al servidor MQTT.
        mqtt.publish(TOPIC_EVT, {"type": "EVENT", "cmd": "BEEP", "val": v})

    # Si el comando no es reconocido.
    else:
        status = "CMD?"
        print("Comando desconocido")


# 1) Conexión a WiFi.
print("Conectando WiFi...")
connect_wifi(WIFI_SSID, WIFI_PASSWORD)
print("WiFi OK")


# 2) Conexión a MQTT.
print("Conectando MQTT...")
mqtt = MqttManager(DEVICE_ID, MQTT_BROKER, MQTT_PORT, on_msg)
mqtt.connect_subscribe(TOPIC_CMD)   # Nos suscribimos al canal de comandos.
print("MQTT OK | Subscrito a:", TOPIC_CMD)


# Bucle principal: el dispositivo corre sin parar.
while True:
    mqtt.check()   # Revisamos si llegaron nuevos comandos.

    # Leemos sensores y mostramos en pantalla OLED.
    try:
        d = sensors.read()
    except Exception as e:
        print("Error leyendo sensores:", e)
        # Si falla, usamos valores por defecto.
        d = {"temp_c": 0, "hum_pct": 0, "light_pct": 0, "ts": int(time.time())}

    try:
        acts.show(d, status=status)   # Mostramos datos en la pantalla OLED.
    except Exception as e:
        print("Error OLED/actuators:", e)

    # Publicamos telemetría cada cierto tiempo (definido en config.py).
    if time.time() - last_pub >= TELE_INTERVAL_SEC:
        mqtt.publish(TOPIC_TELE, d)   # Enviamos datos de sensores al servidor MQTT.
        last_pub = time.time()
        status = "PUB"
        print("Publicado telemetría:", d, "->", TOPIC_TELE)

    time.sleep(1)   # Esperamos 1 segundo antes de repetir el ciclo.
