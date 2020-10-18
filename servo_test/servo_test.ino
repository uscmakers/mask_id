#include <Servo.h>

Servo servo;
int angle = 0;

void servoSetup() {
  // put your setup code here, to run once:
  servo.attach(7);
  servo.write(angle);
}

void servoLoop() {
  // put your main code here, to run repeatedly:
  for(angle = 10; angle < 180; angle++)  
  {                                  
    servo.write(angle);               
    delay(15);                   
  } 
  // now scan back from 180 to 0 degrees
  for(angle = 180; angle > 10; angle--)    
  {                                
    servo.write(angle);           
    delay(15);       
  }
}
