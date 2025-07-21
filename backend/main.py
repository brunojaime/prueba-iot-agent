from fastapi import FastAPI
import paho.mqtt.client as mqtt
import os
import ssl
import json
import uuid
from dotenv import load_dotenv

load_dotenv()

# MQTT config desde variables de entorno
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
CA_CERT = os.getenv("CA_CERT")
CLIENT_CERT = os.getenv("CLIENT_CERT")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
TEMP_TOPIC = os.getenv("TEMP_TOPIC")
LED_TOPIC = os.getenv("LED_TOPIC")

# Estado compartido
last_temperature = None
last_humidity = None
last_time = None
last_led_status = None

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    print(f"✅ Conectado a MQTT con código {rc}")
    client.subscribe(TEMP_TOPIC)
    print(f"📡 Suscripto a {TEMP_TOPIC}")

def on_message(client, userdata, msg):
    global last_temperature, last_humidity, last_time, last_led_status
    try:
        data = json.loads(msg.payload.decode())
        print("📥 Payload recibido:", data)
        if "temperature" in data:
            last_temperature = data["temperature"]
        if "humidity" in data:
            last_humidity = data["humidity"]
        if "time" in data:
            last_time = data["time"]
        if "LED" in data:
            last_led_status = data["LED"]
    except Exception as e:
        print("⚠️ Error al parsear mensaje MQTT:", e)

# Inicializar cliente MQTT
mqtt_client = mqtt.Client(client_id=f"fastapi-{uuid.uuid4()}")
mqtt_client.tls_set(ca_certs=CA_CERT, certfile=CLIENT_CERT, keyfile=PRIVATE_KEY, tls_version=ssl.PROTOCOL_TLSv1_2)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

print("🔌 Conectando al broker MQTT...")
mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
mqtt_client.loop_start()
print("🚀 MQTT client iniciado")

# Iniciar FastAPI normalmente
app = FastAPI()

@app.get("/temperature")
def get_temperature():
    return {
        "temperature": last_temperature,
        "humidity": last_humidity,
        "time": last_time,
        "led_status": last_led_status
    }

@app.post("/led/{state}")
def set_led(state: str):
    state = state.upper()
    if state not in ["LED_ON", "LED_OFF", "LEER_DATOS"]:
        return {"error": "Invalid state"}
    mqtt_client.publish(LED_TOPIC, state)
    return {"status": f"LED set to {state}"}
