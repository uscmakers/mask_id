#include <SPI.h>
#include <WiFiNINA.h>
//#include "arduino_secrets.h" // Create an arduino_secrets.h file and define the SECRET_SSID and SECRET_PASS
// with the WiFi properties of the network
#include <Servo.h>

int mask_flag = 1;
int lock_flag = 1;
char ssid[] = "ATT8T56pbr 2.4ghz"; // your network SSID (name)
char pass[] = "7emn9+bq9kab"; // your network password (use for WPA, or use as key for WEP)

// Replace host and port with host and port of RPi
const char * host = "192.168.1.101";
const uint16_t port = 5000;
String message = "ON";
int status = WL_IDLE_STATUS;
const int pinSwitch = 12;  //Pin Reed
const int pinLed    = 9;  //Pin LED
int StatoSwitch = 0;
const int REED_PIN = 2; // Pin connected to reed switch
const int LED_PIN = 13; // LED pin - active-high



WiFiClient client;

void setup() {
  // put your setup code here, to run once:
  wifiSetup();
  //reedSwitch_setup() 
  servoSetup();
  mask_flag = 1;
  lock_flag = 1; 
}

void loop() {
  // put your main code here, to run repeatedly:
  wifiLoop();
  
//  prox = reed_loop() 
//  servoLoop(prox);
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
      
  // if there are incoming bytes available

  // from the server, read them and print them:
  while (client.available()) {

    char c = client.read();
    message = message + c; 
    Serial.write(c);

  }
  
//  if (message  == "ON"){
//    mask_flag = 1;
//    message = "OFF";
//    
//  }
//  else if(message == "OFF"){
//    mask_flag = 0;
//  }

  if (!client.connected()) {
    
  // if the server's disconnected, stop the client:

    Serial.println();

    Serial.println("disconnecting from server.");

    client.stop();

    // do nothing forevermore:

    while (true);

  }
}



//https://learn.sparkfun.com/tutorials/reed-switch-hookup-guide/all
void reedSwitch_setup() 
{
  // Since the other end of the reed switch is connected to ground, we need
  // to pull-up the reed switch pin internally.
  pinMode(REED_PIN, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);
}

int reed_loop() 
{
  int proximity = digitalRead(REED_PIN); // Read the state of the switch
  if (proximity == LOW) // If the pin reads low, the switch is closed.
  {
    Serial.println("Switch closed");
    delay(1000);
   
  }
  else
  {
    Serial.println("switch open");
    delay(1000);

  }

  return proximity;
}






Servo servo;
int angle = 0;

void servoSetup() {
  // put your setup code here, to run once:
  servo.attach(7);
  servo.write(angle);
 
}

void servoLoop(int proximity) {
  // put your main code here, to run repeatedly:
  Serial.println(mask_flag);
  Serial.println(lock_flag);
  
  if (mask_flag == 1 && lock_flag == 1){
    Serial.println("mask on door locked");
    Serial.println(StatoSwitch);
    delay(1000);
    if(proximity == LOW){
      Serial.print("lock open");
      for(angle = 10; angle < 180; angle++) {                                  
        servo.write(angle);               
        delay(15);                   
       } 
    }
    //mask_flag = 0;
  }
  // check if the door is unlocked and door is closed
  // then lock the lock
  else if(lock_flag == 0 && proximity == LOW){
    // now scan back from 180 to 0 degrees
    Serial.print("lock closed");
    for(angle = 180; angle > 10; angle--){                                
      servo.write(angle);           
      delay(15);       
    }
    //maybe add alarm if door is left open 
    
  }
//  
//  for(angle = 10; angle < 180; angle++)  
//  {                                  
//    servo.write(angle);               
//    delay(15);                   
//  } 
//  // now scan back from 180 to 0 degrees
//  for(angle = 180; angle > 10; angle--)    
//  {                                
//    servo.write(angle);           
//    delay(15);       
//  }
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
