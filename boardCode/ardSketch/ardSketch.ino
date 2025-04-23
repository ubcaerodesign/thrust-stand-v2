#define VPin 11
#define IPin 10
#define DOUT1 A2
#define SCK1 A3
#define DOUT2 A4
#define SCK2 A5

uint8_t analog_reference = DEFAULT;

int offset;

#include "HX711.h"
#include "wiring_private.h"

HX711 scale1;
HX711 scale2;

void setup() {
  Serial.begin(9600);

  Serial.println("STARTING");

  scale1.begin(DOUT1, SCK1);
  scale1.set_scale();
  scale1.tare();

  scale2.begin(DOUT2, SCK2);
  scale2.set_scale();
  scale2.tare();

  long timeStart = millis();
  int count = 0;
  double sumC = 0;
  while (timeStart + 100 > millis()) {
    sumC += analogReadCustom(IPin);
    count++;
  }
  offset = sumC / count * -1;

  Serial.println("STARTED");
}

void loop() {
  if (scale1.is_ready()) {
    long reading = scale1.read();
    Serial.print("Load Cell 1: ");
    long weight = (reading - 243452 + 13475) / 220.9;
    Serial.print(weight);
    Serial.print(" ");
  } else {
    Serial.println("Scale1 not ready");
  }

  /*if (scale2.is_ready()) {
    long reading = scale2.read();
    long weight = reading - 226700;
    Serial.print("Load Cell 2: ");
    Serial.print(weight);
    Serial.print(" ");
  } else {
    Serial.println("Scale2 not ready");
  }*/

  long timeStart = millis();
  int count = 0;
  double sumC = 0;
  double sumV = 0;
  while (timeStart + 100 > millis()) {
    int iSense = analogReadCustom(IPin) + offset;
    sumC += iSense * (5.0 / 1023.0 * 10);
    int vSense = analogReadCustom(VPin);
    sumV += vSense * (5.0 / 1023.0 * 6);
    count++;
  }
  float current = sumC / count;
  float voltage = sumV / count;
  Serial.print("Voltage: ");
  Serial.print(voltage);
  Serial.print("V  ");
  Serial.print("Current: ");
  Serial.print(current);
  Serial.println("A");
  delay(400);
}

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
  #if defined(__AVR_ATtiny25__) || defined(__AVR_ATtiny45__) || defined(__AVR_ATtiny85__)
    ADMUX = (analog_reference << 4) | (pin & 0x07);
  #else
    ADMUX = (analog_reference << 6) | (pin & 0x07);
  #endif
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