#include <SPI.h>
#include <WiFiNINA.h>
#include "arduino_secrets.h" // Create an arduino_secrets.h file and define the SECRET_SSID and SECRET_PASS
// with the WiFi properties of the network

char ssid[] = ""; // your network SSID (name)
char pass[] = ""; // your network password (use for WPA, or use as key for WEP)

// Replace host and port with host and port of RPi
const char * host = "192.168.1.219";
const uint16_t port = 5000;

int status = WL_IDLE_STATUS;

WiFiClient client;

void wifiSetup() {
    // check for the WiFi module:

  if (WiFi.status() == WL_NO_MODULE) {

    Serial.println("Communication with WiFi module failed!");

    // don't continue

    while (true);

  }

  String fv = WiFi.firmwareVersion();

  if (fv < WIFI_FIRMWARE_LATEST_VERSION) {

    Serial.println("Please upgrade the firmware");

  }

  // attempt to connect to Wifi network:

  while (status != WL_CONNECTED) {

    Serial.print("Attempting to connect to SSID: ");

    Serial.println(ssid);

    // Connect to WPA/WPA2 network. Change this line if using open or WEP network:

    status = WiFi.begin(ssid, pass);

    // wait 10 seconds for connection:

    delay(10000);

  }

  Serial.println("Connected to wifi");

  printWifiStatus();

  Serial.println("\nStarting connection to server...");

  // if you get a connection, report back via serial:

  if (client.connect(host, port)) {
    
    Serial.println("connected to server");
    
  }
}

void wifiLoop() {
      
  // if there are incoming bytes available

  // from the server, read them and print them:

  while (client.available()) {

    char c = client.read();

    Serial.write(c);

  }

  if (client.connected()) {
    
    client.println("Sending message from client");
    
    delay(10000);
    
  } else { // if the server's disconnected, stop the client:

    Serial.println();

    Serial.println("disconnecting from server.");

    client.stop();

    // do nothing forevermore:

    while (true);

  }
}

void setup()
{

  Serial.begin(9600);
  while (!Serial) {} // Wait for serial port to connect. Needed for native USB port only.

}

void loop()
{

}

void printWifiStatus() {

  // print the SSID of the network you're attached to:

  Serial.print("SSID: ");

  Serial.println(WiFi.SSID());

  // print your board's IP address:

  IPAddress ip = WiFi.localIP();

  Serial.print("IP Address: ");

  Serial.println(ip);

  // print the received signal strength:

  long rssi = WiFi.RSSI();

  Serial.print("signal strength (RSSI):");

  Serial.print(rssi);

  Serial.println(" dBm");
}
