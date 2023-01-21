# Writer interface over umqtt API.

from umqtt.robust import MQTTClient
import json
import LED

MESSAGE = b''

def sub_cb(topic, msg):
    global MESSAGE
    print((topic, msg))
    MESSAGE=msg
    if msg == b'on':
        LED.LED.on()
    if msg == b'off':
        LED.LED.off()


class MQTTlocal:
  __slots__ = ('host', 'port', 'topic', 'client')
  def __init__(self, name, host, port, pub_topic, sub_topic):
    self.sub_topic = sub_topic
    self.pub_topic = pub_topic
    self.host = host
    self.port = port
    self.client = MQTTClient(name, host, port)
    self.client.set_callback(sub_cb)
    self._connect()
    self.client.subscribe(topic=self.sub_topic)

  def _connect(self):
    print("Connecting to %s:%s" % (self.host, self.port))
    self.client.connect()
    print("Connection successful")

  def publish(self, x):
    data = bytes(json.dumps(x), 'utf-8')
    self.client.publish(bytes(self.pub_topic, 'utf-8'), data)

  def on_completed(self):
    print("mqtt_completed, disconnecting")
    self.client.disconnect()

  def on_error(self, e):
    print("mqtt on_error: %s, disconnecting" %e)
    self.client.disconnect()

  def check_msg(self):
    self.client.check_msg()

  def last_msg(self):
    global MESSAGE
    return(str(MESSAGE, 'utf-8'))
