import paho.mqtt.client as mqtt

broker_address = "localhost"
topic = "watchover/alerts"

def send_alert(message):
    client = mqtt.Client()
    client.connect(broker_address, 1883, 60)
    client.publish(topic, message)
    client.disconnect()