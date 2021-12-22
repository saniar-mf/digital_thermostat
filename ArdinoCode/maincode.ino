/*
Auth : Saniar_Mf
my github : https://github.com/saniar-mf
 */ 


//importing librarys
#include <Arduino.h>
#include <U8g2lib.h>
#include <SPI.h>
#include <Wire.h>
#include <EEPROM.h>

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>

#include <OneWire.h>
#include <DallasTemperature.h>

//Defining Ports and Protocols
#define ONE_WIRE_BUS 2

#define Buzzer 13
#define Heater 6
#define Cooler 4

#define Volume A0

#define ModeSW 8
#define ChangeSW 7


OneWire oneWire(ONE_WIRE_BUS);

DallasTemperature sensors(&oneWire);

U8G2_SSD1306_128X32_UNIVISION_F_HW_I2C u8g2(U8G2_R0);//Connected to arduino I2C

//Main Values
float Temp1;
float MaxTemp;
float MinTemp;

bool Alarm = 0;
bool BHeater = 0;
bool BCooler = 0;

char AdAlarm = 0;
char AdBH = 1;
char AdBC = 2;

char AdMax = 3;
char AdMin = 8;

bool Place = 0;
char Item = 0;

float TempLog[8];

uint8_t Status = 115;


//this function make Temp string from temprature value to make show able in display
void getString(char *str){
    char s[20];
    char *sign = "-";
    if (Temp1>=0){
        sign = "";
    }
    int d = abs(Temp1);
    int a = (int)((fabs(Temp1) - (float)d)*10);
    sprintf(s,"%s%d.%d",sign,d,a);
    strcpy(str,s);
}
//this function make Min\Max string from values to make show able in display
void getMaxMin(char *Max,char* Min){
    char MaxStr[10];
    char MinStr[10];
    
    char *signM = "-";
    char *signm = "-";
    
    if (MaxTemp>=0.0){
        signM = "";
    }
    if (MinTemp>=0.0){
        signm = "";
    }
    
    int dM = abs((int)MaxTemp);
    int aM = (int)((fabs(MaxTemp) - (float)dM)*10);
    sprintf(MaxStr,"%s%d.%d",signM,dM,aM);

    int dm = abs((int)MinTemp);
    int am = (int)((fabs(MinTemp) - (float)dm)*10);
    sprintf(MinStr,"%s%d.%d",signm,dm,am);

    strcpy(Min,MinStr);
    strcpy(Max,MaxStr);
    
}

void setup(void) {
  pinMode(Buzzer, OUTPUT);
  pinMode(Heater, OUTPUT);
  pinMode(Cooler, OUTPUT);
  //This Codes is for checking EEPROM and if was True it means that this is first start afret uploading code and after putting default valuess in EEPROM
  if(EEPROM.read(0)==255 and EEPROM.read(1)==255 and EEPROM.read(2)==255){
      EEPROM.put(AdMax,30.0);
      EEPROM.put(AdMin,20.0);
      EEPROM.put(AdAlarm,1);
      EEPROM.put(AdBH,1);
      EEPROM.put(AdBC,1);
      delay(400);
  }
  //Getting Values from EEPROM memory
  EEPROM.get(AdMax, MaxTemp);
  EEPROM.get(AdMin, MinTemp);
  EEPROM.get(AdAlarm, Alarm);
  EEPROM.get(AdBH, BHeater);
  EEPROM.get(AdBC, BCooler);
  //main start up
  u8g2.begin();
  sensors.begin();
  u8g2.clearBuffer();          // clear the internal memory
  u8g2.setFont(u8g2_font_logisoso18_tr );  //suitable fonts from https://github.com/olikraus/u8g2/wiki/fntlistall
  u8g2.drawStr(10, 30, "Saniar_Mf");
  u8g2.sendBuffer();         // transfer internal memory to the display
 digitalWrite(Heater,LOW);
 digitalWrite(Cooler,HIGH);
 digitalWrite(Buzzer,LOW);
 delay(100);
 digitalWrite(Buzzer,Alarm);
 delay(100);
 digitalWrite(Buzzer,LOW);
 delay(100);
 digitalWrite(Buzzer,Alarm);
 delay(100);
 digitalWrite(Buzzer,LOW);
 delay(200);
 digitalWrite(Heater,HIGH);
 digitalWrite(Cooler,LOW);
 digitalWrite(Buzzer,Alarm);
 u8g2.clearBuffer();          // clear the internal memory
 u8g2.setFont(u8g2_font_logisoso18_tr );
 u8g2.drawStr(30, 30, "Ready");
 u8g2.sendBuffer();
  sensors.requestTemperatures();
  Temp1 = sensors.getTempCByIndex(0);
  for(int i = 0;i<8;i++){
      TempLog[i] = Temp1;
  }
  
  delay(100);
  digitalWrite(Buzzer,LOW);
  digitalWrite(Cooler,LOW);
  digitalWrite(Heater,LOW);

}

void loop(void) {
  if (Place == 0){//in main meno
     if (digitalRead(ModeSW)==1){
        delay(30);
        if (digitalRead(ModeSW)==1){
          Place = 1;
          delay(70);
          Setting();
        }
     }
     else{
        MainSC();
        delay(500);
     }
  }
  else if (Place == 1){//in Setting Meno
    if(digitalRead(ModeSW)==1){
        delay(30);
        if(digitalRead(ModeSW)==1){
          Item += 1;
          delay(70);
        }
    }
    Setting();
  }
}

void Setting()
{
    sensors.requestTemperatures();
    Temp1 = sensors.getTempCByIndex(0);
    u8g2.clearBuffer();
    char MaxStr[10];
    char MinStr[10];
    getMaxMin(MaxStr, MinStr);
    u8g2.setFont(u8g2_font_lubB08_tr);
    u8g2.drawStr(3, 12, "Max: ");
    unsigned char width = u8g2.getStrWidth("Max: ");
    u8g2.drawStr(width, 12, MaxStr);
    u8g2.drawStr(3, 31, "Min: ");
    u8g2.drawStr(width, 31, MinStr);
    if (u8g2.getStrWidth(MaxStr) >= u8g2.getStrWidth(MinStr))
    {
        width += u8g2.getStrWidth(MaxStr);
    }
    else
    {
        width += u8g2.getStrWidth(MinStr);
    }

    if (Item == 0)
    { //MaxTemp
        int VolumeV = (analogRead(Volume) / 4)-128;
        if (VolumeV - 1 > MinTemp)
        {
            MaxTemp = VolumeV;
        }
        u8g2.drawRFrame(1, 1, width + 1, 15, 1);
        //Drawing Frame
    }
    else if (Item == 1)
    { //MinTemp
        int VolumeV = (analogRead(Volume) / 4)-128;
        if (VolumeV + 1 < MaxTemp)
        {
            MinTemp = VolumeV;
        }
        u8g2.drawRFrame(1, 19, width + 1, 15, 1);
    }
    else if (Item == 2)
    { //Alarm
        u8g2.drawRFrame(width + 7, 5, 22, 22, 1);
        if (digitalRead(ChangeSW) == 1)
        {
            delay(40);
            if (digitalRead(ChangeSW) == 1)
            {
                if (Alarm == 1)
                {
                    Alarm = 0;
                    digitalWrite(Buzzer, LOW);
                }
                else
                {
                    Alarm = 1;
                }
                delay(160);
            }
        }
    }
    else if (Item == 3)
    { //Heater
        u8g2.drawRFrame(width + 30, 5, 22, 22, 1);
        if (digitalRead(ChangeSW) == 1)
        {
            delay(40);
            if (digitalRead(ChangeSW) == 1)
            {
                if (BHeater == 1)
                {
                    BHeater = 0;
                    digitalWrite(Heater, LOW);
                }
                else
                {
                    BHeater = 1;
                }
                delay(160);
            }
        }
    }
    else if (Item == 4)
    { //Cooler
        u8g2.drawRFrame(width + 51, 5, 22, 22, 1);
        if (digitalRead(ChangeSW) == 1)
        {
            delay(40);
            if (digitalRead(ChangeSW) == 1)
            {
                if (BCooler == 1)
                {
                    BCooler = 0;
                    digitalWrite(Cooler, LOW);
                }
                else
                {
                    BCooler = 1;
                }
                delay(160);
            }
        }
    }

    //Drawing Icons
    u8g2.setFont(u8g2_font_open_iconic_all_2x_t);
    // Alarm: Sound:277 mute:279 - Heater: on=259 off=223  Coller: on=71 off=121
    width += 5;
    if (Alarm == 1)
    {
        u8g2.drawGlyph(width + 4, 24, 277);
    }
    else
    {
        u8g2.drawGlyph(width + 4, 24, 279);
    }

    if (BHeater == 1)
    {
        u8g2.drawGlyph(width + 28, 24, 259);
    }
    else
    {
        u8g2.drawGlyph(width + 28, 24, 223);
    }

    if (BCooler == 1)
    {
        u8g2.drawGlyph(width + 50, 24, 71);
    }
    else
    {
        u8g2.drawGlyph(width + 50, 24, 121);
    }
    ApplyOuts();
    u8g2.sendBuffer();
    if (Item == 5)
    {
        EEPROM.put(AdMax, MaxTemp);
        EEPROM.put(AdMin, MinTemp);
        EEPROM.put(AdAlarm, Alarm);

        EEPROM.put(AdBH, BHeater);
        EEPROM.put(AdBC, BCooler);
        Place = 0;
        Item = 0;
        u8g2.clearBuffer();
        u8g2.setFont(u8g2_font_open_iconic_all_2x_t);
        u8g2.drawGlyph(48, 32, 120);
        u8g2.sendBuffer();
        delay(400);
    }
}


void MainSC() {
  sensors.requestTemperatures();
  Temp1 = sensors.getTempCByIndex(0);
  
  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_logisoso18_tr);
  
  char str[15];
  getString(str);
  int width_temp = u8g2.getStrWidth(str);
  
  u8g2.drawStr(1, 30, str);
  u8g2.setFont(u8g2_font_7x13B_tf);
  u8g2.drawUTF8(width_temp + 3, 32, "°C");

  char Max[10];
  char Min[10];
  getMaxMin(Max,Min);
  
  u8g2.setFont(u8g2_font_open_iconic_all_1x_t);

  u8g2.drawGlyph(width_temp+24, 10, 119); //Max 
  u8g2.drawGlyph(width_temp+24, 31, 116); //Min
  
   // Iconfonts up = 76 down = 73  ok = 115  bad = 121,283   mute = 279  sun = 259  fan = 71

  ApplyOuts();
  // Drawing icons

  if(Alarm==1){
    u8g2.drawGlyph(4, 9, 277); //Sound
   }
  else{
    u8g2.drawGlyph(4, 9, 279); 
   }

  if (BHeater==1){
    u8g2.drawGlyph(16, 9, 259); 
  }
  else{
    u8g2.drawGlyph(16, 9, 223); 
  }
  if (BCooler==1){
    u8g2.drawGlyph(28, 9, 71); 
  }
  else{
    u8g2.drawGlyph(28, 9, 121);
  }
  u8g2.drawGlyph(40, 9, Status);
  u8g2.setFont(u8g2_font_7x13B_tf);
  u8g2.drawStr(width_temp+34,10,Max);
  u8g2.drawStr(width_temp+34,32,Min);
  
  u8g2.sendBuffer();
}
void ApplyOuts()
{

    if (Temp1 >= MaxTemp)
    {//temprature is higher than max value -1
        Status = 121;
            digitalWrite(Buzzer, Alarm);
            digitalWrite(Cooler, BCooler);
        digitalWrite(Heater, LOW);
    }
    else if (Temp1 <= MinTemp)
    {//temprature is lower than max value +1
        Status = 280;

            digitalWrite(Buzzer, Alarm);

            digitalWrite(Heater, BHeater);

        digitalWrite(Cooler, LOW);
    }
    else if (Temp1 > MaxTemp - ((MaxTemp - MinTemp) / 3))
    {//this means starting cooling when temp is les than 1/3 avrage max-min
        Status = 73;
            digitalWrite(Cooler, BCooler);
        digitalWrite(Heater, LOW);
        digitalWrite(Buzzer, LOW);
    }
    else if (Temp1 < MinTemp + ((MaxTemp - MinTemp) / 3))
    { 
        Status = 76;
        if (BHeater == 1)
        {
            digitalWrite(Heater, HIGH);
        }
        digitalWrite(Cooler, LOW);

        digitalWrite(Buzzer, LOW);
    }

    else
    {
        float temp = TempLog[0];
        for (int i = 0; i < 7; i++)
            TempLog[i] = TempLog[i + 1];
        TempLog[7] = temp;
        if(((TempLog[0]+TempLog[1]+TempLog[2]+TempLog[3])-(TempLog[4]+TempLog[5]+TempLog[6]+TempLog[7])) >0 and Temp1 < (MaxTemp-MinTemp)/2){//Ro be kahesh
            if (BHeater == 1)
            {
                digitalWrite(Heater, HIGH);
                digitalWrite(Cooler, LOW);
            }
        }
        else if(((TempLog[0]+TempLog[1]+TempLog[2]+TempLog[3])-(TempLog[4]+TempLog[5]+TempLog[6]+TempLog[7])) < 0 and Temp1 > (MaxTemp-MinTemp)/2){//Ro be AfZayesh
            if (BCooler == 1)
            {
                digitalWrite(Cooler, HIGH);
                digitalWrite(Heater, LOW);
            }
        }
        else{
            digitalWrite(Buzzer, LOW);
            digitalWrite(Cooler, LOW);
            digitalWrite(Heater, LOW);
        }
        Status = 115;

    }
}
