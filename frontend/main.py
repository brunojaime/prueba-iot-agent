from nicegui import ui
import requests
import os
from datetime import datetime, timedelta


BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Labels
humidity_label = ui.label("Humidity: ---").classes("text-lg")
time_label = ui.label("Time: ---").classes("text-lg")
temperature_label = ui.label("Temperature: ---").classes("text-lg")
led_status_label = ui.label("LED Status: ---").classes("text-lg")

# LED icon (dynamic)
led_icon = ui.icon('lightbulb-off').classes('text-yellow-500 text-5xl')

def send_led_command(command: str):
    try:
        response = requests.post(f"{BACKEND_URL}/led/{command}")
        ui.notify(response.json().get('status', 'Unknown response'))
    except Exception as e:
        ui.notify(f"Error: {e}")

def update_temperature():
    try:
        response = requests.get(f'{BACKEND_URL}/temperature')
        data = response.json()

        temperature_label.text = f"🌡️ Temperature: {data['temperature']}°C"
        humidity_label.text = f"💧 Humidity: {data['humidity']}%"
        raw_time = data['time']
        # Detecta si viene en segundos o milisegundos
        if raw_time > 1e12:
            dt = datetime.fromtimestamp(raw_time / 1000)
        elif raw_time > 1e9:
            dt = datetime.fromtimestamp(raw_time)
        else:
            dt = datetime.now()  # fallback
        dt = dt - timedelta(hours=3)
        time_label.text = f"⏰ Last Updated: {dt.strftime('%d %b %Y, %H:%M')}"
        led_status_label.text = f"💡 LED Status: {data['led_status']}"

        if data['led_status'] == "ON":
            led_icon.name = "lightbulb"
            led_icon.classes('text-yellow-400 text-5xl')
        else:
            led_icon.name = "lightbulb-off"
            led_icon.classes('text-black-400 text-5xl')
    except Exception as e:
        temperature_label.text = ""
        humidity_label.text = ""
        time_label.text = ""
        led_status_label.text = ""
        led_icon.name = "lightbulb-off"
        led_icon.classes('text-gray-400 text-5xl')

# UI Layout
with ui.card().classes('w-full max-w-md mx-auto mt-10 shadow-xl border border-gray-200'):
    ui.label("Device Control Panel").classes('text-3xl font-bold mb-4 text-center text-blue-700')

    with ui.row().classes("justify-center mb-4"):
        led_icon

    with ui.column().classes("gap-2"):
        ui.button("🔆 Turn ON LED", on_click=lambda: send_led_command("LED_ON")).classes('bg-green-500 text-white hover:bg-green-600')
        ui.button("💤 Turn OFF LED", on_click=lambda: send_led_command("LED_OFF")).classes('bg-red-500 text-white hover:bg-red-600')
        ui.button("📥 Read Temp from Device", on_click=lambda: send_led_command("LEER_DATOS")).classes('bg-blue-500 text-white hover:bg-blue-600')

    with ui.separator():
        pass

    with ui.column().classes("mt-4 gap-1"):
        temperature_label
        humidity_label
        time_label
        led_status_label

# Auto update every 5 seconds
ui.timer(5.0, update_temperature)

ui.run(title="IoT Control Panel")
