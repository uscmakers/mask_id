#include <Servo.h>

Servo servo;
int angle = 80;

void setup() {
  // put your setup code here, to run once:
  servo.attach(7);
  servo.write(angle);
}

void loop() {
  // put your main code here, to run repeatedly:
//  servo.write(0);
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
