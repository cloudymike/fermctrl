# Writer interface over umqtt API.
import machine
from umqtt.robust import MQTTClient
import json
import LED


MESSAGE = b''

def sub_cb(topic, msg):
    global MESSAGE
    MESSAGE = msg
    print((topic, MESSAGE))





class MQTTReader:
    __slots__ = ('host', 'port', 'topic', 'client')
    def __init__(self, name, host, port, topic):
        self.topic = topic
        self.host = host
        self.port = port
        self.client = MQTTClient(name, host, port)
        self.client.set_callback(sub_cb)

        self._connect()

        self.client.subscribe(topic=self.topic)

    def _connect(self):
        print("Connecting to %s:%s" % (self.host, self.port))
        self.client.connect()
        print("Connection successful")

    def on_completed(self):
        print("mqtt_completed, disconnecting")
        self.client.disconnect()

    def on_error(self, e):
        print("mqtt on_error: %s, disconnecting" %e)
        self.client.disconnect()

    def disconnect(self):
        self.client.disconnect()

    def wait_msg(self):
        self.client.wait_msg()

    def check_msg(self):
        self.client.check_msg()

    def last_msg(self):
        return(str(MESSAGE, 'utf-8'))
