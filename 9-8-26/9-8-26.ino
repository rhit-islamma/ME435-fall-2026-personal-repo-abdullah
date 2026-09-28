
String inputString = "";      
bool stringComplete = false;  

void setup() {
  Serial.begin(19200);
  inputString.reserve(200); // reserve 200 bytes for the inputString:
}

void loop() {
  // print the string when a newline arrives:
  if (stringComplete) {
    if (inputString.equals("RESET")) {
      delay(500);
      Serial.println("READY, SAGIAN PE Loader, ROM Ver. 1.1.6 12APR2001");
      
    } else if (inputString.startsWith("MOVE")) {
      delay(1500);
      Serial.println("The LED is now off!");
      Serial.println(inputString); 
    }

    // TODO: do the command

    inputString = "";
    stringComplete = false;
  }
}


void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    
    if (inChar == '\n') {
      stringComplete = true;
    } else { 
      inputString += inChar;
    }

    
  }
}

