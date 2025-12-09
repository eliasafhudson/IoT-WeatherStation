import json, time
import paho.mqtt.client as mqtt  # Librería para conectarse a un servidor MQTT (mensajes entre dispositivos).
from db import insert_reading, insert_event  # Funciones para guardar datos en la base de datos.


# Creamos la clase MqttWorker.
class MqttWorker:
    def __init__(self, host, port, topic_tele, topic_evt):
        # Esta función se ejecuta al crear un nuevo "trabajador MQTT".
        # Recibe la dirección del servidor (host), el puerto y los temas (canales) de telemetría y eventos.
        self.host, self.port = host, port
        self.topic_tele, self.topic_evt = topic_tele, topic_evt
        # Creamos un cliente MQTT que se encargará de conectarse y escuchar mensajes.
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

        # Definimos qué funciones se usarán cuando nos conectemos y cuando llegue un mensaje.
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        # Guardamos la última telemetría recibida (inicialmente no hay nada).
        self.last_telemetry = None

    def on_connect(self, client, userdata, flags, reason_code, properties=None):
        # Esta función se ejecuta cuando logramos conectarnos al servidor MQTT.
        # Nos suscribimos a los temas de telemetría y eventos para recibir mensajes.
        client.subscribe(self.topic_tele)
        client.subscribe(self.topic_evt)

    def on_message(self, client, userdata, msg):
        # Esta función se ejecuta cada vez que llega un mensaje por MQTT.
        payload = json.loads(msg.payload.decode("utf-8"))  # Convertimos el mensaje en un diccionario (JSON).

        # Si el mensaje pertenece al tema de telemetría (datos de sensores).
        if msg.topic == self.topic_tele:
            insert_reading(payload)  # Guardamos la lectura en la base de datos.
            self.last_telemetry = payload  # Actualizamos la última telemetría recibida.
        else:
            # Si el mensaje pertenece al tema de eventos.
            # Guardamos el evento en la base de datos con su hora, tipo y detalles.
            insert_event(payload.get("ts", int(time.time())), payload.get("type", "event"), payload)

    def start(self):
        # Esta función inicia la conexión con el servidor MQTT y comienza a escuchar mensajes.
        self.client.connect(self.host, self.port, keepalive=60)
        self.client.loop_start()  # Inicia un bucle en segundo plano para recibir mensajes continuamente.
