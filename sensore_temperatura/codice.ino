#include <DHT.h>
#include <ESP8266WiFi.h>

/* DHT Pro Shield
 * Depends on Adafruit DHT Arduino library
 * https://github.com/adafruit/DHT-sensor-library
 */
#define DHTPIN 2     // questo è il PIN a cui è connesso il sensore (è scritto sullo shield)

// togliere il commento dalla riga del sensore corretto (io uso AM2302)
//#define DHTTYPE DHT11   // DHT 11
#define DHTTYPE DHT22   // DHT 22  (AM2302)
//#define DHTTYPE DHT21   // DHT 21 (AM2301)

// dati della WiFi
const char* ssid     = "[nome rete wifi]"; 
const char* password = "[password wifi]";

// Crare una nuovsa istanza del sensore
DHT dht(DHTPIN, DHTTYPE);


void setup() {
  Serial.begin(9600);
  Serial.println("Sto inziando a lavorare");

  // inizializzare la WiFi e aspettanre la connessione
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    Serial.println(WiFi.localIP());
  }

  // inizializzare il sensore DHT
  dht.begin();
}

void loop() {
  // legge il valore di umidità
  float h = dht.readHumidity();
  // legge la temperatura in Celsius
  float t = dht.readTemperature();
  
  // Se qualcosa è andato storto avvisa
  if (isnan(h) || isnan(t)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  // scrivo i valori su seriale per debug
  Serial.print("Humidity: ");
  Serial.print(h);
  Serial.print(" %\t");
  Serial.print("Temperature: ");
  Serial.print(t);
  Serial.println(" *C ");

  // creo la connessione http per scrivere i valori sul DB
  WiFiClient client;
  if (!client.connect("123.123.123.123", 8000)) { //IP e porta su cui asolta il server web
    Serial.println("Conection Fail");
    return;
  }
    // creo il link completo per la rihciesta HTTP
    String url = "GET /?tab=temp&a=5&t=";
    url += t;
    url += "&h=";
    url += h;
    url += " HTTP/1.1\r\n";
    // Faccio la chiamata http
    client.println(url);
    // la scrivo su seriale per debug
    Serial.println(url);
   
    delay(4000);
    Serial.print("sleep mode");
    // mando la scheda in sleep mode
    // iol valore è espresso in microsecondi
    ESP.deepSleep(1200 * 1000000);
}
