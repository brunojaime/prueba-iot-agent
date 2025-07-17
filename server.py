from fastapi import FastAPI
import paho.mqtt.client as mqtt

app = FastAPI()

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
TEMP_TOPIC = "yourhome/wemos1/temperature"
LED_TOPIC = "yourhome/wemos1/led"

last_temperature = None

def on_connect(client, userdata, flags, rc):
    client.subscribe(TEMP_TOPIC)

def on_message(client, userdata, msg):
    global last_temperature
    if msg.topic == TEMP_TOPIC:
        last_temperature = msg.payload.decode()

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
mqtt_client.loop_start()

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

