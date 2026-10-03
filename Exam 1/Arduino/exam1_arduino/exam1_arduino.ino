void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available()) {
    String inputString = Serial.readStringUntil('\n');

    if (inputString == "LED ON") {
      digitalWrite(LED_BUILTIN, HIGH);
      Serial.println("LED On");
    }

    else if (inputString == "LED OFF") {
      digitalWrite(LED_BUILTIN, LOW);
      Serial.println("LED Off");
    }

    else if (inputString.startsWith("FLASH ")) {
      String args = inputString.substring(6);
      int spaceIndex = args.indexOf(" ");

      int numFlashes = args.substring(0, spaceIndex).toInt();
      int periodMs = args.substring(spaceIndex + 1).toInt();

      Serial.print("Flashes = ");
      Serial.print(numFlashes);
      Serial.print("  PeriodMs = ");
      Serial.println(periodMs);

      for (int i = 0; i < numFlashes; i++) {
        digitalWrite(LED_BUILTIN, HIGH);
        delay(periodMs / 2);

        digitalWrite(LED_BUILTIN, LOW);
        delay(periodMs / 2);
      }
    }
  }
}