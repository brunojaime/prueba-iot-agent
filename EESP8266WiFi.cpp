#include <ESP8266WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <DHT.h>


// certs.h

const char* ca_cert = R"EOF(
-----BEGIN CERTIFICATE-----
[AQUÍ VA EL CONTENIDO DE AmazonRootCA1.pem]
-----END CERTIFICATE-----
)EOF";

const char* client_cert = R"EOF(
-----BEGIN CERTIFICATE-----
[AQUÍ VA EL CONTENIDO DE certificate.pem.crt]
-----END CERTIFICATE-----
)EOF";

const char* private_key = R"EOF(
-----BEGIN RSA PRIVATE KEY-----
[AQUÍ VA EL CONTENIDO DE private.pem.key]
-----END RSA PRIVATE KEY-----
)EOF";


// Wifi
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// AWS IoT endpoint (lo encontrás en la consola de AWS IoT Core)
const char* mqtt_server = "";  //enpoint.txt
const int mqtt_port = 8883;

// Topics
const char* tempTopic = "yourhome/wemos1/temperature";
const char* ledTopic = "yourhome/wemos1/led";

// Certificados (deben subirse al ESP como archivos SPIFFS o embebidos como strings en código)
extern const char* ca_cert;     // AmazonRootCA1.pem
extern const char* client_cert; // certificate.pem.crt
extern const char* private_key; // private.pem.key

// DHT
#define DHTPIN D4
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

// LED
#define LEDPIN D2

WiFiClientSecure net;
PubSubClient client(net);

void setup_wifi() {
  delay(10);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  String command = "";
  for (unsigned int i = 0; i < length; i++) {
    command += (char)payload[i];
  }

  if (String(topic) == ledTopic) {
    digitalWrite(LEDPIN, command == "ON" ? HIGH : LOW);
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Connecting to AWS IoT...");
    String clientId = "Wemos-" + String(random(0xffff), HEX);
    if (client.connect(clientId.c_str())) {
      Serial.println("Connected");
      client.subscribe(ledTopic);
    } else {
      Serial.print("Failed. rc=");
      Serial.print(client.state());
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

  // Set SSL/TLS certificates
  net.setCACert(ca_cert);
  net.setCertificate(client_cert);
  net.setPrivateKey(private_key);

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
  if (now - lastMsg > 5000) {
    lastMsg = now;
    float t = dht.readTemperature();
    float h = dht.readHumidity();
    if (!isnan(t)) {
      char payload[64];
      snprintf(payload, sizeof(payload), "{\"temp\":%.2f,\"hum\":%.2f}", t, h);
      client.publish(tempTopic, payload);
      Serial.println(payload);
    }
  }
}
