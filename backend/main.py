import os, time, json
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
BASE_DIR = os.path.dirname(__file__)

# Importamos la nueva función insert_event
from db import init_db, insert_reading, log_command, insert_event 
from thingspeak import write_channel, execute_talkback

load_dotenv(os.path.join(BASE_DIR, ".env"))

DEVICE_ID = os.getenv("DEVICE_ID", "ws-esp32-001")
MQTT_HOST = os.getenv("MQTT_HOST", "broker.emqx.io")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

THINGSPEAK_WRITE_KEY = os.getenv("THINGSPEAK_WRITE_KEY")
TALKBACK_ID = os.getenv("TALKBACK_ID")
TALKBACK_API_KEY = os.getenv("TALKBACK_API_KEY")

TOPIC_TELE = f"iot/weather/{DEVICE_ID}/telemetry"
TOPIC_CMD  = f"iot/weather/{DEVICE_ID}/cmd"
TOPIC_EVT  = f"iot/weather/{DEVICE_ID}/event"  ### NUEVO: Definir tema de eventos

last_tele = None
last_ts_write = 0

def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"Conectado a MQTT ({MQTT_HOST}). Suscribiendo...")
    client.subscribe(TOPIC_TELE)
    client.subscribe(TOPIC_EVT) ### NUEVO: Suscribirse a eventos
    print(f"Suscrito a: {TOPIC_TELE} y {TOPIC_EVT}")

def on_message(client, userdata, msg):
    global last_tele
    try:
        d = json.loads(msg.payload.decode("utf-8"))
        
        # 1. Si es Telemetría
        if msg.topic == TOPIC_TELE:
            last_tele = d
            insert_reading(d)
            print("[TELE] Guardado:", d)
            
        # 2. Si es un Evento (Confirmación del ESP32) ### NUEVO BLOQUE
        elif msg.topic == TOPIC_EVT:
            # Asumimos que el ESP32 manda algo como {"type":"EVENT", "cmd":"LED", ...}
            ts = d.get("ts", int(time.time()))
            evt_type = d.get("type", "INFO")
            insert_event(ts, evt_type, d)
            print("[EVENTO] Registrado:", d)
            
    except Exception as e:
        print("Error procesando mensaje MQTT:", e)

def publish_cmd(cmd_string):
    payload = {"value": cmd_string}
    # Nota: Crear un cliente nuevo por mensaje es ineficiente, 
    # pero aceptable para esta escala.
    pub = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    pub.connect(MQTT_HOST, MQTT_PORT, 60)
    pub.publish(TOPIC_CMD, json.dumps(payload))
    pub.disconnect()

def process_simple(d):
    alerts = []
    if d.get("temp_c", 0) >= 32:
        alerts.append("HOT")
    if d.get("light_pct", 100) <= 20:
        alerts.append("DARK")
    return alerts

def main():
    global last_ts_write
    print("Iniciando Backend System...")
    init_db() # Crea las tablas si no existen

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_start()

    print("Backend corriendo. Presiona Ctrl+C para salir.")

    while True:
        # 1) Enviar a ThingSpeak (>=15s por limit)
        if last_tele and (time.time() - last_ts_write) >= 16: # Subí a 16s por seguridad
            alerts = process_simple(last_tele)
            try:
                write_channel(THINGSPEAK_WRITE_KEY, last_tele)
                last_ts_write = time.time()
                print(f"[TS] Update OK | Alerts: {alerts}")
            except Exception as e:
                print("[TS] Error enviando:", e)

        # 2) Leer comando desde TalkBack y enviarlo al device
        try:
            tb = execute_talkback(TALKBACK_ID, TALKBACK_API_KEY)
            cmd_str = (tb.get("command_string") or "").strip()
            if cmd_str:
                publish_cmd(cmd_str)
                log_command(cmd_str, "published_to_device")
                print("[CMD] Procesado desde TalkBack:", cmd_str)
        except Exception as e:
            print("[CMD] Error consultando TalkBack:", e)

        time.sleep(5)

if __name__ == "__main__":
    main()
