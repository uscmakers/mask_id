//------------------------------------//
//             Created by             //
//         Alessio Bigini 2015        //
//       http://alessiobigini.it      //
//------------------------------------//
const int pinSwitch = 12;  //Pin Reed
const int pinLed    = 9;  //Pin LED
int StatoSwitch = 0;

void reedSwitchSetup() {
  pinMode(pinLed, OUTPUT);      //Imposto i PIN
  pinMode(pinSwitch, INPUT);
}

void reedSwitchLoop()
{
  StatoSwitch = digitalRead(pinSwitch);  //Leggo il valore del Reed
  if (StatoSwitch == HIGH)
  {
    digitalWrite(pinLed, HIGH);
  }
  else
  {
    digitalWrite(pinLed, LOW);
  }
}
