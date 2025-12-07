import json, time
import paho.mqtt.client as mqtt
from db import insert_reading, insert_event

class MqttWorker:
    def __init__(self, host, port, topic_tele, topic_evt):
        self.host, self.port = host, port
        self.topic_tele, self.topic_evt = topic_tele, topic_evt
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.last_telemetry = None

    def on_connect(self, client, userdata, flags, reason_code, properties=None):
        client.subscribe(self.topic_tele)
        client.subscribe(self.topic_evt)

    def on_message(self, client, userdata, msg):
        payload = json.loads(msg.payload.decode("utf-8"))
        if msg.topic == self.topic_tele:
            insert_reading(payload)
            self.last_telemetry = payload
        else:
            insert_event(payload.get("ts", int(time.time())), payload.get("type","event"), payload)

    def start(self):
        self.client.connect(self.host, self.port, keepalive=60)
        self.client.loop_start()
