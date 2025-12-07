import ujson
from umqtt.simple import MQTTClient

class MqttManager:
    def __init__(self, client_id, host, port, on_msg):
        self.client = MQTTClient(client_id=client_id, server=host, port=port, keepalive=60)
        self.client.set_callback(on_msg)

    def connect_subscribe(self, topic_cmd):
        self.client.connect()
        self.client.subscribe(topic_cmd)

    def publish(self, topic, payload_dict):
        self.client.publish(topic, ujson.dumps(payload_dict))

    def check(self):
        self.client.check_msg()
