from fastapi import FastAPI
from contextlib import asynccontextmanager
import paho.mqtt.client as mqtt
import os
import ssl
from dotenv import load_dotenv

load_dotenv()

MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
CA_CERT = os.getenv("CA_CERT")
CLIENT_CERT = os.getenv("CLIENT_CERT")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
TEMP_TOPIC = os.getenv("TEMP_TOPIC")
LED_TOPIC = os.getenv("LED_TOPIC")

last_temperature = None

def on_connect(client, userdata, flags, rc):
    print(f"Conectado a MQTT con código {rc}")
    client.subscribe(TEMP_TOPIC)
    print(f"Suscripto a {TEMP_TOPIC}")

def on_message(client, userdata, msg):
    global last_temperature
    print(f"Mensaje recibido en topic {msg.topic}: {msg.payload.decode()}")
    print(f"Payload crudo: {msg.payload}")
    print("Callback ejecutado")
    if msg.topic == TEMP_TOPIC:
        last_temperature = msg.payload.decode()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global mqtt_client
    mqtt_client = mqtt.Client(client_id="fastapi-server")
    mqtt_client.tls_set(
        ca_certs=CA_CERT,
        certfile=CLIENT_CERT,
        keyfile=PRIVATE_KEY,
        tls_version=ssl.PROTOCOL_TLSv1_2
    )
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    print("Conectando al broker MQTT...")
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
    mqtt_client.loop_start()
    print("MQTT client started")
    yield
    print("Cerrando conexión MQTT...")
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    print("MQTT client stopped")

app = FastAPI(lifespan=lifespan)

@app.get("/temperature")
def get_temperature():
    if last_temperature is not None:
        return {"temperature": last_temperature}
    return {"error": "No data yet"}

@app.post("/led/{state}")
def set_led(state: str):
    if state.upper() not in ["ON", "OFF"]:
        return {"error": "State must be ON or OFF"}
    mqtt_client.publish(LED_TOPIC, state.upper())
    return {"status": f"LED set to {state.upper()}"}
