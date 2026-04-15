import paho.mqtt.client as mqtt

class AdafruitPublisher:
    def __init__(self, user, key):
        self.user = user
        self.client = mqtt.Client()
        self.client.username_pw_set(user, key)
        self.broker = "io.adafruit.com"

    def connect(self):
        self.client.connect(self.broker, 1883, 60)
        self.client.loop_start()

    def publish(self, feed_name, value):
        topic = f"{self.user}/feeds/{feed_name}"
        result = self.client.publish(topic, value)
        if result.rc == 0:
            print(f"[>] {feed_name}: {value}")
        else:
            print("[!] Error al publicar")

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()