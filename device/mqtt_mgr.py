import ujson                         # Librería para manejar datos en formato JSON (texto estructurado).
from umqtt.simple import MQTTClient  # Librería ligera para conectarse a un servidor MQTT en MicroPython.


# Clase MqttManager: se encarga de manejar la conexión MQTT.
class MqttManager:
    def __init__(self, client_id, host, port, on_msg):
        # Esta función se ejecuta al crear un nuevo objeto MqttManager.
        # Configura el cliente MQTT con:
        # - client_id: nombre único del dispositivo.
        # - host: dirección del servidor MQTT.
        # - port: puerto de conexión.
        # - keepalive: tiempo máximo para mantener la conexión activa.
        self.client = MQTTClient(client_id=client_id, server=host, port=port, keepalive=60)
        # Definimos la función que se ejecutará cada vez que llegue un mensaje.
        self.client.set_callback(on_msg)

    def connect_subscribe(self, topic_cmd):
        # Esta función conecta el dispositivo al servidor MQTT
        # y se suscribe al canal de comandos (para recibir instrucciones).
        self.client.connect()
        self.client.subscribe(topic_cmd)

    def publish(self, topic, payload_dict):
        # Esta función sirve para ENVIAR un mensaje (publicar) a un canal MQTT.
        # Convierte el diccionario de datos en texto JSON antes de enviarlo.
        self.client.publish(topic, ujson.dumps(payload_dict))

    def check(self):
        # Esta función revisa si hay mensajes nuevos en los canales suscritos.
        # Si llega un mensaje, ejecuta la función definida en set_callback.
        self.client.check_msg()
