#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

// WIFI CONFIGURATION
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// MQTT CONFIGURATION
const char* mqtt_server = "broker.hivemq.com"; // Use a public broker for test
const int mqtt_port = 1883;
const char* mqtt_user = ""; // Not needed for public
const char* mqtt_password = ""; // Not needed for public

// DHT SENSOR CONFIG
#define DHTPIN D4       // GPIO2
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

// LED CONFIG
#define LEDPIN D2      // GPIO4

WiFiClient espClient;
PubSubClient client(espClient);

// Topics
const char* tempTopic = "yourhome/wemos1/temperature";
const char* ledTopic = "yourhome/wemos1/led";

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.print("WiFi connected, IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  // Handle LED commands
  String command = "";
  for (unsigned int i = 0; i < length; i++) {
    command += (char)payload[i];
  }
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("]: ");
  Serial.println(command);

  if (String(topic) == ledTopic) {
    if (command == "ON") {
      digitalWrite(LEDPIN, HIGH);
    } else if (command == "OFF") {
      digitalWrite(LEDPIN, LOW);
    }
  }
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientId = "WemosClient-";
    clientId += String(random(0xffff), HEX);

    // Attempt to connect
    if (client.connect(clientId.c_str(), mqtt_user, mqtt_password)) {
      Serial.println("connected");
      client.subscribe(ledTopic); // Subscribe to LED control topic
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(LEDPIN, OUTPUT);
  digitalWrite(LEDPIN, LOW);

  dht.begin();
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

unsigned long lastMsg = 0;
void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();
  if (now - lastMsg > 5000) { // Send temperature every 5 seconds
    lastMsg = now;
    float t = dht.readTemperature();
    float h = dht.readHumidity();
    if (!isnan(t) && !isnan(h)) {
      char payload[50];
      snprintf(payload, 50, "{\"temp\":%.2f,\"hum\":%.2f}", t, h);
      client.publish(tempTopic, payload);
      Serial.print("Temperature sent: ");
      Serial.println(payload);
    } else {
      Serial.println("Failed to read from DHT sensor!");
    }
  }
}

