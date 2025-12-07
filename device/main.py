print("Hello, ESP32!")


import time
import ujson
from config import *
from wifi_mgr import connect_wifi
from mqtt_mgr import MqttManager
from sensors import Sensors
from actuators import Actuators

print("BOOT: iniciando device...")

sensors = Sensors()
acts = Actuators()

status = "BOOT"
last_pub = 0

def parse_command_string(s: str):
    s = (s or "").strip()
    if not s or "=" not in s:
        return None, None
    k, v = s.split("=", 1)
    return k.strip().upper(), v.strip()

def on_msg(topic, msg):
    global status
    print("MQTT MSG topic:", topic, "raw:", msg)

    try:
        payload = ujson.loads(msg)
        cmd_str = payload.get("value", "")
    except Exception as e:
        print("JSON parse fail:", e)
        cmd_str = msg.decode() if hasattr(msg, "decode") else str(msg)

    print("CMD_STR:", cmd_str)

    k, v = parse_command_string(cmd_str)
    print("PARSED:", k, v)

    # ... dentro de on_msg ...
    if k == "LED":
        acts.set_led(v == "1")
        status = f"LED={v}"
        print("LED ejecutado:", v)
        # CUMPLIMIENTO DE REQUISITO: Reportar evento
        mqtt.publish(TOPIC_EVT, {"type": "EVENT", "cmd": "LED", "val": v})

    elif k == "BEEP":
        acts.beep(ms=int(v))
        status = f"BEEP={v}"
        print("BEEP ejecutado:", v)
        # CUMPLIMIENTO DE REQUISITO: Reportar evento
        mqtt.publish(TOPIC_EVT, {"type": "EVENT", "cmd": "BEEP", "val": v})

    else:
        status = "CMD?"
        print("Comando desconocido")

# 1) WiFi
print("Conectando WiFi...")
connect_wifi(WIFI_SSID, WIFI_PASSWORD)
print("WiFi OK")

# 2) MQTT
print("Conectando MQTT...")
mqtt = MqttManager(DEVICE_ID, MQTT_BROKER, MQTT_PORT, on_msg)
mqtt.connect_subscribe(TOPIC_CMD)
print("MQTT OK | Subscrito a:", TOPIC_CMD)

while True:
    # escucha comandos (no bloqueante)
    mqtt.check()

    # lectura sensores + OLED
    try:
        d = sensors.read()
    except Exception as e:
        print("Error leyendo sensores:", e)
        d = {"temp_c": 0, "hum_pct": 0, "light_pct": 0, "ts": int(time.time())}

    try:
        acts.show(d, status=status)
    except Exception as e:
        print("Error OLED/actuators:", e)

    # publica telemetría cada N segundos
    if time.time() - last_pub >= TELE_INTERVAL_SEC:
        mqtt.publish(TOPIC_TELE, d)
        last_pub = time.time()
        status = "PUB"
        print("Publicado telemetría:", d, "->", TOPIC_TELE)

    time.sleep(1)
