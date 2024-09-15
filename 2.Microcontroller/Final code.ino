#include <Keypad.h>
#include <Servo.h>
#include <EEPROM.h>

int RKey = 0;

const int lightPin = 10;
const int tempPin = A4;
const int pirPin = 9;
const int buzzerPin = A5;
const int redLedPin = A1;
const int greenLedPin = A2;
const int blueLedPin = A3;
const int motorPin1 = 12;
const int motorPin2 = 13;
const int enablePin = 11;
const int servoPin = 8;

const byte ROWS = 4;
const byte COLS = 3;

char keymap[ROWS][COLS] = {
  {'1', '2', '3'},
  {'4', '5', '6'},
  {'7', '8', '9'},
  {'*', '0', '#'}
};

byte rowPins[ROWS] = {7, 6, 5, 4};
byte colPins[COLS] = {3, 2, A0};

Keypad myKeypad = Keypad(makeKeymap(keymap), rowPins, colPins, ROWS, COLS);
Servo doorServo;

const char defaultPassword[] = "1234";
char enteredPassword[5] = ""; // 5 to fit 4 characters and the null terminator
char savedPassword[5] = "";

bool doorLocked = true;

void setup() {
  Serial.begin(9600);
  
  pinMode(tempPin, INPUT);
  pinMode(pirPin, INPUT);
  pinMode(buzzerPin, OUTPUT);
  pinMode(redLedPin, OUTPUT);
  pinMode(greenLedPin, OUTPUT);
  pinMode(blueLedPin, OUTPUT);
  pinMode(motorPin1, OUTPUT);
  pinMode(motorPin2, OUTPUT);
  pinMode(enablePin, OUTPUT);
  pinMode(lightPin, INPUT);
  
  doorServo.attach(servoPin);
  doorServo.write(0);
  
  EEPROM.get(0, savedPassword);
  if (strlen(savedPassword) == 0) {
    strcpy(savedPassword, defaultPassword);  // If no password in EEPROM, use default
  }
  
  Serial.println(F("System ready."));
}

void loop() {
  if (Serial.available()) {
    char command = Serial.read();

    if (command == 'R') {
      RKey = 1;
      Serial.println(F("Received RKey!"));
    } else if (command == 'P') {
      receiveNewPassword();
    }
  }

  if (RKey == 1) {
    Serial.println(F("Open! System functions started."));
    doorLocked = false;
    openDoor();
    runSystemFunctions();  // Continuously check for the stop condition inside this function
  }

  char key = myKeypad.getKey();
  if (key) {
    Serial.print(F("Key pressed: "));
    Serial.println(key);

    if (key == '#') {
      if (strcmp(enteredPassword, savedPassword) == 0) {
        Serial.println(F("Correct password! System functions started."));
        doorLocked = false;
        openDoor();
        runSystemFunctions();  // Keep running system functions until stopped
      } else {
        Serial.println(F("Wrong password!"));
        handleWrongPassword();
      }
      clearPassword();
    } else if (key == '*') {
      clearPassword();
      Serial.println(F("Password cleared."));
    } else {
      appendToPassword(key);
    }
  }

  if (doorLocked && digitalRead(pirPin) == HIGH) {
    Serial.println(F("Motion detected inside while the door is locked!"));
  }

  delay(100);
}

void receiveNewPassword() {
  char newPassword[5];
  int index = 0;

  while (Serial.available()) {
    char c = Serial.read();
    if (index < 4 && isdigit(c)) {
      newPassword[index++] = c;
    }
  }
  newPassword[index] = '\0';

  updatePassword(newPassword);
  Serial.print(F("New password set: "));
  Serial.println(newPassword);
}

void openDoor() {
  doorServo.write(90);
  delay(1000);
  doorLocked = false;
}

void closeDoor() {
  doorServo.write(0);  // Rotate servo to close the door
  delay(1000);

  // Stop the fan
  analogWrite(enablePin, 0);  // Set motor speed to 0 to stop the fan
  digitalWrite(motorPin1, LOW);  // Ensure the motor is off
  digitalWrite(motorPin2, LOW);  // Ensure the motor is off
  digitalWrite(redLedPin, HIGH);
  digitalWrite(greenLedPin, LOW);
  digitalWrite(blueLedPin, LOW);

  doorLocked = true;
  Serial.println(F("System stopped, fan turned off, door closed."));
}

void runSystemFunctions() {
  while (true) {
    int light = digitalRead(lightPin);
    Serial.println(light ? F("Light: Off") : F("Light: ON"));
    
    int tempC = map(analogRead(tempPin), 0, 1023, -55, 125);
    if (tempC > 30) {
      digitalWrite(redLedPin, HIGH);
      digitalWrite(greenLedPin, LOW);
      digitalWrite(blueLedPin, LOW);
    } else if (tempC > 20) {
      digitalWrite(redLedPin, LOW);
      digitalWrite(greenLedPin, HIGH);
      digitalWrite(blueLedPin, LOW);
    } else {
      digitalWrite(redLedPin, LOW);
      digitalWrite(greenLedPin, LOW);
      digitalWrite(blueLedPin, HIGH);
    }

    int motorSpeed = map(tempC, -40, 125, 0, 255);
    analogWrite(enablePin, motorSpeed);
    digitalWrite(motorPin1, LOW);
    digitalWrite(motorPin2, HIGH);

    Serial.print(F("Temperature: "));
    Serial.print(tempC);
    Serial.print(F(" °C, Fan speed: "));
    Serial.println(motorSpeed);

    char key = myKeypad.getKey();
    if (key == '*') {
        Serial.println(F("Stopping system and closing door."));
        closeDoor();
        break;  // Exit the system function loop
    }
  }
}

void handleWrongPassword() {
  tone(buzzerPin, 1000, 500);
  Serial.println(F("Warning: Wrong password entered."));
  doorLocked = true;
}

void clearPassword() {
  memset(enteredPassword, 0, sizeof(enteredPassword));
}

void appendToPassword(char key) {
  size_t len = strlen(enteredPassword);
  if (len < sizeof(enteredPassword) - 1) {
    enteredPassword[len] = key;
    enteredPassword[len + 1] = '\0'; // Null-terminate the string
  }
}

void updatePassword(const char* newPassword) {
  strcpy(savedPassword, newPassword);
  EEPROM.put(0, savedPassword);
  Serial.println(F("Password updated and saved to EEPROM."));
}
