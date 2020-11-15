#include <SPI.h>
#include <WiFiNINA.h>
//#include "arduino_secrets.h" // Create an arduino_secrets.h file and define the SECRET_SSID and SECRET_PASS with the WiFi properties of the network
#include <Servo.h>

Servo servo;
WiFiClient client;
int mask_flag = 0;
int lock_flag = 1;
int prox = 0;
char ssid[] = "SpectrumSetup-B8"; // your network SSID (name)
char pass[] = "strongcar994"; // your network password (use for WPA, or use as key for WEP)

// Replace host and port with host and port of RPi
const char * host = "192.168.1.219";
const uint16_t port = 5007;
String message = "";
int status = WL_IDLE_STATUS;
const int LED_PIN = 8;  //Pin LED
int StatoSwitch = 0;
const int REED_PIN = 11; // Pin connected to reed switch
int angle = 85;

void setup() {
  wifiSetup();
  /* Reed Switch Setup */
  // Since the other end of the reed switch is connected to ground, we need
  // to pull-up the reed switch pin internally.
  pinMode(REED_PIN, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);
  /* Servo Setup */
  servo.attach(7);
  servo.write(angle);
}

void loop() {
  wifiLoop();
  reed_loop();
  servoLoop();
}

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
  // if there are incoming bytes available from the server, read them and print them:
  while (client.available()) {
    char c = client.read();
    message = message + c; 
    Serial.write(c);
  }
  Serial.println(message);
  delay(1000);
  if (message  == "MASK"){
    mask_flag = 1;
    //Serial.println(message);
    delay(2000);
    
  }
  else if(message == "NO MASK"){
    mask_flag = 0;
    //Serial.println(message);
    delay(2000);
  }
  if (!client.connected()) {
    // if the server's disconnected, stop the client:
    Serial.println();
    Serial.println("disconnecting from server.");
    client.stop();
    // do nothing forevermore:
    while (true);
  }
}

int reed_loop() 
{
  prox = digitalRead(REED_PIN); // Read the state of the switch
  if (prox == LOW) // If the pin reads low, the switch is closed.
  {
    digitalWrite(LED_PIN, HIGH); // Turn the LED on
    delay(1000);
  }
  else if(prox == HIGH)
  {
    digitalWrite(LED_PIN, LOW); // Turn the LED on
    delay(1000);
  }
}

void servoLoop() {
  // put your main code here, to run repeatedly:
  Serial.println(mask_flag);
  Serial.println(lock_flag);
  delay(1000);
  if (mask_flag == 1 && lock_flag == 1 && prox == LOW){
    Serial.println("mask on");
    Serial.println("unlock door");
    for(angle = 85; angle >= 0; angle--) {                                  
        servo.write(angle);               
        delay(15);                   
    }
    lock_flag = 0;
    mask_flag = 0;
    message = "";
    delay(5000);
  }
  // check if the door is unlocked and door is closed, then lock the lock
  else if(lock_flag == 0 && prox == LOW){
    // now scan back from 80 to 0 degrees
    Serial.println("lock door ");
    for(angle = 0; angle <= 85; angle++){                                
      servo.write(angle);           
      delay(15);       
    }
    //maybe add alarm if door is left open 
    lock_flag =1;
    delay(2000);
  }
  
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
