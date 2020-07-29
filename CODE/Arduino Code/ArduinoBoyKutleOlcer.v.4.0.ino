#include "HX711.h"
#define DOUT  10
#define CLK  13
HX711 scale;
float calibration_factor = 25620;
#include <LiquidCrystal.h>
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);
const int trigb = 7;
const int trige = 6;
const int echob = A3;
const int echoe = A2;
const int kalibButon = 8;
const int olcmeButon = 9;
const int aktarmaButon = A5;
int sure = 0;
int mesafe = 0;
int ilkmesafe;
int inByte;
int yanliskalibre = 116;

float boy;
float esneklik;
float esneklikderece;
float kutle;

void setup() {
  Serial.begin(9600);
  //Serial.println("CLEARDATA");
  //Serial.println("LABEL,boy(cm),kutle(kg),esneklik(cm),esneklikderece(/10)");
  lcd.begin(16, 2);
  lcd.setCursor(0, 0);
  lcd.print("AKILLI BOY-KUTLE");
  delay(1000);
  lcd.setCursor(0, 1);
  lcd.print("OLCUM SEYSi-AKiF");
  delay(3000);
  lcd.clear();
  scale.begin(DOUT, CLK);
  scale.set_scale();
  scale.tare();
  long zero_factor = scale.read_average();
  pinMode(trigb, OUTPUT);
  pinMode(trige, OUTPUT);
  pinMode(echob, INPUT);
  pinMode(echoe, INPUT);
  pinMode(kalibButon, INPUT);
  pinMode(olcmeButon, INPUT);
  pinMode(aktarmaButon, INPUT);
  while (digitalRead(kalibButon) == LOW) {

    inByte = Serial.read();
    
    lcd.setCursor(0, 0);
    lcd.print("KALiBRASYON iCiN");
    lcd.setCursor(0, 1);
    lcd.print("<-BUTONA BASINIZ");
    delay(100);
    if (digitalRead(kalibButon) == HIGH or inByte == 's') {
      delay(50);
      ilkmesafe = mesafeolcb();
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("KALiBRASYON");
      lcd.setCursor(0, 1);
      lcd.print("YAPILDI : ");
      lcd.print(ilkmesafe);
      lcd.setCursor(13, 1);
      lcd.print("cm");

      Serial.print("calibration");
      
      delay(2000);
      lcd.clear();
      break;
    }
  }
}


void loop() {
  scale.set_scale(calibration_factor);

  inByte = Serial.read();
  
  if (digitalRead(olcmeButon) == HIGH or inByte=='o') {
    lcd.setCursor(0, 0);
    lcd.print("BOYUNUZ:");
    lcd.setCursor(0, 1);
    boy = (ilkmesafe + yanliskalibre) - mesafeolcb();
    lcd.print(boy);
    lcd.setCursor(5, 1);
    lcd.print("cm");
    delay(2000);
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("KUTLENIZ:");
    lcd.setCursor(0, 1);
    kutle = scale.get_units();
    lcd.print(kutle, 3);
    lcd.setCursor(7, 1);
    lcd.print("kg");

    Serial.print("height,");
    Serial.print(boy);
    Serial.print(",");
    Serial.print("scale,");
    Serial.print(kutle);
    
    delay(2000);
    lcd.clear();
  }
  else if (digitalRead(kalibButon) == HIGH or inByte=='k') {
    lcd.setCursor(0, 0);
    lcd.print(" ESNEKLiK OLCUM ");
    lcd.setCursor(0, 1);
    lcd.print("      MODU      ");
    delay(2000);
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("   HEMSTRiNG    ");
    lcd.setCursor(0, 1);
    lcd.print("ESNEKLiK OLCUMU ");
    delay(800);
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("SENSORU 2. KONU-");
    lcd.setCursor(0, 1);
    lcd.print("  MA GETiRiNiZ  ");
    delay(800);
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("AYAKLARINIZI UZ-");
    lcd.setCursor(0, 1);
    lcd.print("ATARAK OTURUNUZ");
    delay(800);
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("VE EGiLEBiLDiGi-");
    lcd.setCursor(0, 1);
    lcd.print("NiZ KADAR EGiLiN");
    delay(800);
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("SiMDi OLCUM iCiN");
    lcd.setCursor(0, 1);
    lcd.print("BUTONA BASINIZ->");

    Serial.print('r');
    
    while (digitalRead(olcmeButon) == LOW){
      inByte = Serial.read();

      if (inByte=='c'){
        break;
        }
      
      delay(10);
    }
    delay(200);
    esneklik = mesafeolce();
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("ESNEKLiK MESAFE:");
    lcd.setCursor(0, 1);
    lcd.print(esneklik);
    lcd.setCursor(6, 1);
    lcd.print("cm");
    delay(5000);
    esneklikderece = (100 - esneklik)/10;
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("ESNEKLiK DERECE:");
    lcd.setCursor(0, 1);
    lcd.print("10 UZERiNDEN");
    lcd.setCursor(13, 1);
    lcd.print(esneklikderece);

    Serial.print("strech,");
    Serial.print(esneklik);
    Serial.print(",");
    Serial.print(esneklikderece);
    
    delay(5000);
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("SiMDi EXCEL iCiN");
    lcd.setCursor(0, 1);
    lcd.print("3.BUTONA BASINIZ");
    delay(2000);
    lcd.clear();
  }
  else if (analogRead(aktarmaButon) > 500 or inByte=='w') {
    writetoexcel(boy, esneklik, esneklikderece);
  }
  else {
      lcd.setCursor(0, 0);
      lcd.print("<-- ESNEKLiK OLC");
      lcd.setCursor(0, 1);
      lcd.print("BOY-KUTLE OLC-->");
      delay(100);
      lcd.clear();
    }
  }

  int mesafeolcb() {
    digitalWrite(trigb, HIGH);
    delay(1);
    digitalWrite(trigb, LOW);
    sure = pulseIn(echob, HIGH);
    mesafe = (sure / 2) / 27.6;
    return mesafe;
  }
  int mesafeolce() {
    digitalWrite(trige, HIGH);
    delay(1);
    digitalWrite(trige, LOW);
    sure = pulseIn(echoe, HIGH);
    mesafe = (sure / 2) / 27.6;
    return mesafe;
  }
  
float writetoexcel(float boy, float esneklik, float esneklikderece) {
    lcd.setCursor(0, 0);
    lcd.print("EXCELE YAZILIYOR...");
    delay(2000);
    lcd.clear();
    //Serial.print("DATA,");

    Serial.print("writemode,");
    
    Serial.print(boy);
    Serial.print(",");
    Serial.print(kutle);
    Serial.print(",");
    Serial.print(esneklik);
    Serial.print(",");
    Serial.println(esneklikderece);

    boy = 0;
    kutle = 0;
    esneklik = 0;
    esneklikderece = 0;
}
