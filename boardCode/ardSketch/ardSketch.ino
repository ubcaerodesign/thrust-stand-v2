#define VPin 11
#define IPin 10
#define DOUT1 A2
#define SCK1 A3
#define DOUT2 A4
#define SCK2 A5
#define THROTTLE 17

#include "HX711.h"
#include "wiring_private.h"
#include <Servo.h>

Servo throttlePwm;

HX711 scale1;
HX711 scale2;

bool lc1 = true;
bool lc2 = true;
bool vtg = true;
bool cur = true;

// controls
// inf: returns board information
// lc1(0-1): send load cell 1 data (0 = false, 1 = true)
// lc2(0-1): send load cell 2 data (0 = false, 1 = true)
// vtg(0-1): send voltage data (0 = false, 1 = true)
// cur(0-1): send current data (0 = false, 1 = true)
// thr(0-100): set esc throttle percentage (number as percentage)
// stp: emergency stop, overrides pwm signal to low

// data
// lc1, lc2: grams
// vtg: volts
// cur: amps
// note, all data sent over serial is not zeroed, simply a raw reading, the computer software does the calibration

// note
// the pin controlling the ESC is on a pin that is by default hard wired to a LED on the leonardo, to override this, go to arduino core and replace:
// #define RXLED0			PORTB |= (1<<0)
// #define RXLED1			PORTB &= ~(1<<0)
// with this:
// #define RXLED0 0
// #define RXLED1 0

void setup() {
  Serial.begin(9600);

  Serial.println("STARTING");

  scale1.begin(DOUT1, SCK1);
  scale1.set_scale();
  scale1.tare();

  scale2.begin(DOUT2, SCK2);
  scale2.set_scale();
  scale2.tare();

  throttlePwm.attach(THROTTLE);
  setThrottle(0);

  Serial.println("STARTED");
}

void loop() {
  // deciphering of the commands is 110% vibecoded
  static String command = "";
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      parseCommand(command);
      command = "";
    } else {
      command += c;
    }
  }

  // reads load cell 1
  long cell1Reading = 0;
  bool cell1Status = false;
  if (scale1.is_ready()) {
    long reading = scale1.read();
    cell1Reading = reading / 220.9; // 220.9 is a calibrated number
    cell1Status = true;
  }

  // reads load cell 2
  long cell2Reading = 0;
  bool cell2Status = false;
  if (scale2.is_ready()) {
    long reading = scale2.read();
    cell2Reading = reading / 220.9; // 220.9 is a calibrated number
    cell2Status = true;
  }

  // reads current and voltage using an average over the last 100ms
  long timeStart = millis();
  int count = 0;
  double sumC = 0;
  double sumV = 0;
  while (timeStart + 100 > millis()) {
    int iSense = analogReadCustom(IPin);
    sumC += iSense * (5.0 / 1023.0 * 10); // refer to altium for current computations
    int vSense = analogReadCustom(VPin);
    sumV += vSense * (5.0 / 1023.0 * 6); // refer to altium for voltage computations
    count++;
  }
  float current = sumC / count;
  float voltage = sumV / count;

  // writes return data according to serial communication
  if (lc1) {
    Serial.print("lc1(");
    if (cell1Status) {
      Serial.print(cell1Reading);
    } else {
      Serial.print("n");
    }
    Serial.println(")");
  }

  if (lc2) {
    Serial.print("lc2(");
    if (cell2Status) {
      Serial.print(cell2Reading);
    } else {
      Serial.print("n");
    }
    Serial.println(")");
  }

  if (vtg) {
    Serial.print("cur(");
    Serial.print(current);
    Serial.println(")");
  }

  if (cur) {
    Serial.print("vtg(");
    Serial.print(voltage);
    Serial.println(")");
  }

  delay(150);
}

void emergencyStop() {

}

void setThrottle(int thr) {
  Serial.print("Throttle set to ");
  Serial.print(thr);
  Serial.println("%");
  throttlePwm.writeMicroseconds(1450 + thr * 10);
}

void info() {

}

// everything below is part of command deciphering and is also 110% vibecoded (too lazy to deal with this)
void parseCommand(const String& cmd) {
  if (cmd == "inf") {
    info();
  } else if (cmd.startsWith("lc1(")) {
    lc1 = extractBool(cmd);
  } else if (cmd.startsWith("lc2(")) {
    lc2 = extractBool(cmd);
  } else if (cmd.startsWith("vtg(")) {
    vtg = extractBool(cmd);
  } else if (cmd.startsWith("cur(")) {
    cur = extractBool(cmd);
  } else if (cmd.startsWith("thr(")) {
    int val = extractNumber(cmd);
    if (val >= 0 && val <= 100) {
      setThrottle(val);
    } else {
      Serial.println("Invalid throttle value");
    }
  } else if (cmd == "stp") {
    emergencyStop();
  } else {
    Serial.println("Unknown command");
  }
}

bool extractBool(const String& s) {
  int start = s.indexOf('(');
  int end = s.indexOf(')');
  if (start != -1 && end != -1 && end > start) {
    int val = s.substring(start + 1, end).toInt();
    return val != 0;
  }
  return false;  // Default
}

int extractNumber(const String& s) {
  int start = s.indexOf('(');
  int end = s.indexOf(')');
  if (start != -1 && end != -1 && end > start) {
    return s.substring(start + 1, end).toInt();
  }
  return -1; // Invalid
}

// taken from arduino source code to bypass pin conversion
uint8_t analog_reference = DEFAULT;
int analogReadCustom(uint8_t pin)
{
    uint8_t low, high;

  #if defined(ADCSRB) && defined(MUX5)
    // the MUX5 bit of ADCSRB selects whether we're reading from channels
    // 0 to 7 (MUX5 low) or 8 to 15 (MUX5 high).
    ADCSRB = (ADCSRB & ~(1 << MUX5)) | (((pin >> 3) & 0x01) << MUX5);
  #endif
    
    // set the analog reference (high two bits of ADMUX) and select the
    // channel (low 4 bits).  this also sets ADLAR (left-adjust result)
    // to 0 (the default).
  #if defined(ADMUX)
    ADMUX = (analog_reference << 6) | (pin & 0x07);
  #endif

    // without a delay, we seem to read from the wrong channel
    //delay(1);

  #if defined(ADCSRA) && defined(ADCL)
    // start the conversion
    sbi(ADCSRA, ADSC);

    // ADSC is cleared when the conversion finishes
    while (bit_is_set(ADCSRA, ADSC));

    // we have to read ADCL first; doing so locks both ADCL
    // and ADCH until ADCH is read.  reading ADCL second would
    // cause the results of each conversion to be discarded,
    // as ADCL and ADCH would be locked when it completed.
    low  = ADCL;
    high = ADCH;
  #else
    // we dont have an ADC, return 0
    low  = 0;
    high = 0;
  #endif

    // combine the two bytes
    return (high << 8) | low;
}