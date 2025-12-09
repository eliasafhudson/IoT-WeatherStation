import os, time, json
import paho.mqtt.client as mqtt  # Librería para conectarse a un servidor MQTT (mensajes entre dispositivos).
from dotenv import load_dotenv  # Librería para leer variables guardadas en un archivo .env (configuración).

BASE_DIR = os.path.dirname(__file__)  # Guardamos la ruta de la carpeta actual.

# Importamos funciones que creamos en db.py
from db import init_db, insert_reading, log_command, insert_event
# Importamos funciones para trabajar con ThingSpeak (plataforma en la nube).
from thingspeak import write_channel, execute_talkback

# Cargamos las variables de configuración desde el archivo .env
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Variables de configuración (si no están en .env, se usan valores por defecto).
DEVICE_ID = os.getenv("DEVICE_ID", "ws-esp32-001")
MQTT_HOST = os.getenv("MQTT_HOST", "broker.emqx.io")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

THINGSPEAK_WRITE_KEY = os.getenv("THINGSPEAK_WRITE_KEY")
TALKBACK_ID = os.getenv("TALKBACK_ID")
TALKBACK_API_KEY = os.getenv("TALKBACK_API_KEY")

# Definimos los "temas" de comunicación MQTT (como canales de radio).
TOPIC_TELE = f"iot/weather/{DEVICE_ID}/telemetry"  # Donde el dispositivo manda datos de sensores.
TOPIC_CMD = f"iot/weather/{DEVICE_ID}/cmd"  # Donde enviamos comandos al dispositivo.
TOPIC_EVT = f"iot/weather/{DEVICE_ID}/event"  # Donde el dispositivo manda eventos especiales.

last_tele = None  # Aquí guardaremos la última telemetría recibida.
last_ts_write = 0  # Aquí guardaremos el último momento en que enviamos datos a ThingSpeak.


# ---------------- FUNCIONES ----------------

def on_connect(client, userdata, flags, reason_code, properties=None):
    # Esta función se ejecuta cuando logramos conectarnos al servidor MQTT.
    print(f"Conectado a MQTT ({MQTT_HOST}). Suscribiendo...")
    # Nos suscribimos a los temas de telemetría y eventos para recibir mensajes.
    client.subscribe(TOPIC_TELE)
    client.subscribe(TOPIC_EVT)
    print(f"Suscrito a: {TOPIC_TELE} y {TOPIC_EVT}")


def on_message(client, userdata, msg):
    # Esta función se ejecuta cada vez que llega un mensaje por MQTT.
    global last_tele
    try:
        d = json.loads(msg.payload.decode("utf-8"))  # Convertimos el mensaje en un diccionario (JSON).

        # 1. Si el mensaje es de telemetría (datos de sensores).
        if msg.topic == TOPIC_TELE:
            last_tele = d  # Guardamos la última telemetría recibida.
            insert_reading(d)  # La guardamos en la base de datos.
            print("[TELE] Guardado:", d)

        # 2. Si el mensaje es un evento (ejemplo: confirmación de acción del ESP32).
        elif msg.topic == TOPIC_EVT:
            ts = d.get("ts", int(time.time()))  # Hora del evento (si no viene, usamos la actual).
            evt_type = d.get("type", "INFO")  # Tipo de evento (ejemplo: "LED encendido").
            insert_event(ts, evt_type, d)  # Guardamos el evento en la base de datos.
            print("[EVENTO] Registrado:", d)

    except Exception as e:
        print("Error procesando mensaje MQTT:", e)


def publish_cmd(cmd_string):
    # Esta función sirve para ENVIAR un comando al dispositivo (ESP32).
    payload = {"value": cmd_string}
    pub = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    pub.connect(MQTT_HOST, MQTT_PORT, 60)
    pub.publish(TOPIC_CMD, json.dumps(payload))  # Publicamos el comando en el tema correspondiente.
    pub.disconnect()


def process_simple(d):
    # Esta función revisa los datos de sensores y genera alertas simples.
    alerts = []
    if d.get("temp_c", 0) >= 32:  # Si la temperatura es mayor o igual a 32°C.
        alerts.append("HOT")  # Agregamos alerta de calor.
    if d.get("light_pct", 100) <= 20:  # Si la luz es menor o igual a 20%.
        alerts.append("DARK")  # Agregamos alerta de oscuridad.
    return alerts


def main():
    # Esta es la función principal que arranca todo el sistema.
    global last_ts_write
    print("Iniciando Backend System...")
    init_db()  # Crea las tablas de la base de datos si no existen.

    # Creamos el cliente MQTT y configuramos sus funciones.
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_start()  # Iniciamos el bucle para escuchar mensajes.

    print("Backend corriendo. Presiona Ctrl+C para salir.")

    # Bucle infinito: el sistema corre todo el tiempo.
    while True:
        # 1) Enviar datos a ThingSpeak cada 16 segundos (mínimo permitido).
        if last_tele and (time.time() - last_ts_write) >= 16:
            alerts = process_simple(last_tele)  # Revisamos si hay alertas.
            try:
                write_channel(THINGSPEAK_WRITE_KEY, last_tele)  # Enviamos datos a ThingSpeak.
                last_ts_write = time.time()
                print(f"[TS] Update OK | Alerts: {alerts}")
            except Exception as e:
                print("[TS] Error enviando:", e)

        # 2) Revisar si hay comandos en TalkBack y enviarlos al dispositivo.
        try:
            tb = execute_talkback(TALKBACK_ID, TALKBACK_API_KEY)
            cmd_str = (tb.get("command_string") or "").strip()
            if cmd_str:
                publish_cmd(cmd_str)  # Enviamos el comando al ESP32.
                log_command(cmd_str, "published_to_device")  # Lo registramos en la base de datos.
                print("[CMD] Procesado desde TalkBack:", cmd_str)
        except Exception as e:
            print("[CMD] Error consultando TalkBack:", e)

        time.sleep(5)  # Esperamos 5 segundos antes de repetir el ciclo.


# Este bloque asegura que si ejecutamos este archivo directamente, se corre la función main().
if __name__ == "__main__":
    main()
