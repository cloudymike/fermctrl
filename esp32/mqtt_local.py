# Writer interface over umqtt API.

from umqtt.robust import MQTTClient
import json
import LED

MESSAGE = b''

def sub_cb(topic, msg):
    global MESSAGE
    MESSAGE = msg
    print((topic,msg))


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

  def on_next(self, x):
    data = bytes(json.dumps(x), 'utf-8')
    self.client.publish(bytes(self.pub_topic, 'utf-8'), data)

  # Wrapper
  def publish(self, message):
    topic = '/devices/{}/{}'.format(config.google_cloud_config['device_id'], 'events')
    self.client.publish(self.pub_topic('utf-8'), message.encode('utf-8'))

  def on_completed(self):
    print("mqtt_completed, disconnecting")
    self.client.disconnect()

  def on_error(self, e):
    print("mqtt on_error: %s, disconnecting" %e)
    self.client.disconnect()

  def check_msg(self):
    print("Check messages")
    self.client.check_msg()

  def last_msg(self):
    return(str(MESSAGE, 'utf-8'))
