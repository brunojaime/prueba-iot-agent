import paho.mqtt.client as mqtt
import os
import ssl
from dotenv import load_dotenv
import time

load_dotenv()

MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
CA_CERT = os.getenv("CA_CERT")
CLIENT_CERT = os.getenv("CLIENT_CERT")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
TEMP_TOPIC = os.getenv("TEMP_TOPIC")
LED_TOPIC = os.getenv("LED_TOPIC")

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    if rc != 0:
        print("Connection failed, check certificates and endpoint")

def on_publish(client, userdata, mid):
    print(f"Message {mid} published.")

client = mqtt.Client(client_id="python-publisher")
client.tls_set(
    ca_certs=CA_CERT,
    certfile=CLIENT_CERT,
    keyfile=PRIVATE_KEY,
    tls_version=ssl.PROTOCOL_TLSv1_2
)
client.on_connect = on_connect
client.on_publish = on_publish

print("Connecting to broker...")
client.connect(MQTT_BROKER, MQTT_PORT)
client.loop_start()

# Publicar temperatura
temperature_value = "26.7"
result = client.publish(TEMP_TOPIC, temperature_value)
print(f"Publishing temperature {temperature_value} to topic {TEMP_TOPIC}")

# Publicar estado LED
led_state = "OFF"
result = client.publish(LED_TOPIC, led_state)
print(f"Publishing LED state {led_state} to topic {LED_TOPIC}")

time.sleep(2)  # esperar a que se publiquen los mensajes

client.loop_stop()
client.disconnect()
print("Disconnected from broker.")
