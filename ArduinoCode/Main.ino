/*

Auth : Saniar_Mf
My Github : https://github.com/saniar-mf

*/

// importing librarys
#include <Arduino.h>
#include <EEPROM.h>
#include <SPI.h>
#include <U8g2lib.h>
#include <Wire.h>

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <DallasTemperature.h>
#include <OneWire.h>

// Defining Ports and Protocols
#define ONE_WIRE_BUS 2

#define Buzzer 13
#define Heater 6
#define Cooler 4

#define Volume A0
#define SourceVoltage A7 //we don't need this in this project

#define ModeSW 8
#define ChangeSW 7

OneWire oneWire(ONE_WIRE_BUS);

DallasTemperature TempSensors(&oneWire);

U8G2_SSD1306_128X32_UNIVISION_F_HW_I2C u8g2(U8G2_R0); // Connected to arduino I2C

// Main Values
float Temp1;
float MaxTemp;
float MinTemp;

bool Alarm = 0;
bool HeaterState = 0;
bool CoolerState = 0;

bool Place = 0;
uint8_t Item = 0;

float TempLog[8];
uint8_t SN = 123;
uint8_t Status = 91;
uint8_t BTStatus = 53;
bool PowerSave = 0;
//EEPROM Memory address
const char AdAlarm = 0;
const char AdHS = 1;
const char AdCS = 2;

const char AdMax = 3;
const char AdMin = 8;

void setup(void)
{
    Serial.begin(9600);

    pinMode(Buzzer, OUTPUT);
    pinMode(Heater, OUTPUT);
    pinMode(Cooler, OUTPUT);
    pinMode(SourceVoltage, INPUT);

    Serial.write(SN);
    Serial.println("SettingUp");
    bool BT = 0;
    // This Codes is for checking EEPROM and if was True it means that this is first start afret uploading code and after putting default valuess in EEPROM
    if (EEPROM.read(0) == 255 and EEPROM.read(1) == 255 and EEPROM.read(2) == 255)
    {
        EEPROM.put(AdMax, 30.0);
        EEPROM.put(AdMin, 20.0);
        EEPROM.put(AdAlarm, 1);
        EEPROM.put(AdHS, 1);
        EEPROM.put(AdCS, 1);
        EEPROM.put(14, BT); // if battery was low and mcu reset all the time when checking relays
        Serial.println("FirstStart");
        delay(400);
    }
    // Getting Values from EEPROM memory
    EEPROM.get(AdMax, MaxTemp);
    EEPROM.get(AdMin, MinTemp);
    EEPROM.get(AdAlarm, Alarm);
    EEPROM.get(AdHS, HeaterState);
    EEPROM.get(AdCS, CoolerState);
    EEPROM.get(14, BT);
    // main start up
    u8g2.begin();
    TempSensors.begin();
    u8g2.clearBuffer();                    // clear the internal memory
    u8g2.setFont(u8g2_font_logisoso18_tr); // suitable fonts from https://github.com/olikraus/u8g2/wiki/fntlistall
    u8g2.drawStr(10, 30, "Saniar_Mf");
    u8g2.sendBuffer(); // transfer internal memory to the display

    if (BT == 0 || GetBattery() <= 3.75)
    {
        BatteryLow();
    }

    digitalWrite(Heater, LOW);
    digitalWrite(Cooler, HIGH);
    digitalWrite(Buzzer, LOW);
    delay(100);
    digitalWrite(Buzzer, Alarm);
    delay(100);
    digitalWrite(Buzzer, LOW);
    delay(100);
    digitalWrite(Buzzer, Alarm);
    delay(100);
    digitalWrite(Buzzer, LOW);
    delay(200);
    digitalWrite(Heater, HIGH);
    digitalWrite(Cooler, LOW);
    digitalWrite(Buzzer, Alarm);
    u8g2.setPowerSave(PowerSave);
    u8g2.clearBuffer();
    u8g2.drawStr(30, 30, "Ready");
    u8g2.sendBuffer();
    TempSensors.requestTemperatures();
    Temp1 = TempSensors.getTempCByIndex(0);
    if(Temp1<=-126){
        InsertSensor();
    }
    for (int i = 0; i < 8; i++)
    {
        TempLog[i] = Temp1;
    }

    delay(100);
    digitalWrite(Buzzer, LOW);
    digitalWrite(Cooler, LOW);
    digitalWrite(Heater, LOW);
    Serial.println("Ready");
    delay(100);
    EEPROM.put(14, 1);
}

void loop(void)
{
    // Serial.println(GetBattery());
    if (GetBattery() <= 3.75)
    {
        BatteryLow();
    }
    if (Serial.available() > 0)
    {
        SerialParser();
    }
    if (Place == 0)
    { // in main meno
        if (digitalRead(ModeSW) == 1)
        {
            delay(30);
            if (digitalRead(ModeSW) == 1)
            {
                Place = 1;
                delay(70);
                Setting();
            }
        }
        else
        {
            MainSC();
            delay(500);
        }
    }
    else if (Place == 1)
    { // in Setting Meno
        if (digitalRead(ModeSW) == 1)
        {
            delay(30);
            if (digitalRead(ModeSW) == 1)
            {
                Item += 1;
                delay(70);
            }
        }
        Setting();
    }
}

// this function make Temp string from temprature value to make show able in display
void getString(char *str)
{
    char s[7];
    char *sign = "-";
    if (Temp1 >= 0)
    {
        sign = "";
    }
    int d = abs(Temp1);
    int a = (int)((fabs(Temp1) - (float)d) * 10);
    snprintf(s, 7, "%s%d.%d", sign, d, a);
    strcpy(str, s);
}
// this function make Min\Max string from values to make show able in display
void getMaxMin(char *Max, char *Min)
{
    char MaxStr[7];
    char MinStr[7];

    char *signM = "-";
    char *signm = "-";

    if (MaxTemp >= 0.0)
    {
        signM = "";
    }
    if (MinTemp >= 0.0)
    {
        signm = "";
    }

    int dM = abs((int)MaxTemp);
    int aM = (int)((fabs(MaxTemp) - (float)dM) * 10);
    snprintf(MaxStr, 7, "%s%d.%d", signM, dM, aM);

    int dm = abs((int)MinTemp);
    int am = (int)((fabs(MinTemp) - (float)dm) * 10);
    snprintf(MinStr, 7, "%s%d.%d", signm, dm, am);

    strcpy(Min, MinStr);
    strcpy(Max, MaxStr);
}
void SerialParser()
{
    String DATA = Serial.readString();
    // PostMethod = Set+MaxTemp+MinTemp+AlarmState+HeaterState+CoolerState+PowerSavingMode
    // GetMethod =i will send:SN+Temp+MinTemp+MaxTemp+AlarmState+HeaterState+CoolerState+VccVoltage+PowerSavingMode
    String Pieces[7] = {"Set", "200", "200", "2", "2", "2","2"};
    Pieces[0] = DATA.substring(0, DATA.indexOf("+"));

    uint8_t lastIndex = DATA.indexOf("+"), i = 1;

    while (lastIndex < DATA.length() and i < 7)
    {
        Pieces[i] = DATA.substring(lastIndex + 1, DATA.indexOf("+", lastIndex + 1));
        lastIndex = DATA.indexOf("+", lastIndex + 1);
        i++;
    }

    if (Pieces[0] == "Set")
    {
        if (Pieces[1].toInt() < 125 && Pieces[1].toInt() > -50)
        { // MaxTemp
            
            MaxTemp = Pieces[1].toInt();
            float DF = MaxTemp - MinTemp;
            if (DF <= 1)
            {
                MinTemp = MaxTemp - 1;
            }
        }
        if (Pieces[2].toInt() < 125 && Pieces[2].toInt() > -50)
        { // MinTemp
            MinTemp = Pieces[2].toInt();
            float DF = MaxTemp - MinTemp;
            if (DF <= 1)
            {
                MaxTemp = MinTemp + 1;
            }
        }
        if (Pieces[3].toInt() < 2 && Pieces[3].toInt() >= 0)
        { // Alarm State
            Alarm = Pieces[3].toInt();
        }
        if (Pieces[4].toInt() < 2 && Pieces[4].toInt() >= 0)
        { // Heater State
            HeaterState = Pieces[4].toInt();
        }
        if (Pieces[5].toInt() < 2 && Pieces[5].toInt() >= 0)
        { // Cooler State
            CoolerState = Pieces[5].toInt();
        }
        if (Pieces[6].toInt() < 2 && Pieces[6].toInt() >= 0)
        { // Cooler State
            PowerSave = Pieces[6].toInt();
            u8g2.setPowerSave(PowerSave);
        }
        WriteEEPROM();
    }
    else if (Pieces[0] == "Get")
    { 
        if(Pieces[1]=="T"){
          String infos = String(SN)+"+"+String(Temp1);          
          Serial.println(infos);
        }
        else{

        
      // 7% of memory!!!
        //       send:SN+Temp+MinTemp+MaxTemp+AlarmState+HeaterState+CoolerState+VccVoltage+PowerSavingMode
        String infos = String(SN)+"+"+String(Temp1)+"+"+String(MaxTemp)+"+"+String(MinTemp)+"+"+String(Alarm)+"+"+String(HeaterState)+"+"+String(CoolerState)+"+"+(GetBattery())+"+"+String(PowerSave);
        Serial.println(infos);
        // Serial.println("ST+123");
        // Serial.println(Temp1);
        // Serial.println(MaxTemp);
        // Serial.println(MinTemp);
        // Serial.println(Alarm);
        // Serial.println(HeaterState);
        // Serial.println(CoolerState);
        // Serial.println(GetBattery());
        // Serial.println("End+123");
    }
    }
}
void InsertSensor(){
    delay(200);
    TempSensors.requestTemperatures();
    Temp1 = TempSensors.getTempCByIndex(0);
    if(Temp1<=-126){
        u8g2.clearBuffer();
        u8g2.setFont(u8g2_font_profont12_tr);
        u8g2.drawStr(16, 22, "!Insert DS18B20!");
        u8g2.sendBuffer();
        digitalWrite(Heater, LOW);
        digitalWrite(Cooler, LOW);
        Serial.println("SensorDetached");
        bool al = 0;
        while (1)
        {
            digitalWrite(Buzzer,al);
            al = !al;
            TempSensors.requestTemperatures();
            Temp1 = TempSensors.getTempCByIndex(0);
            if(Temp1>=-125){
                break;
            }
            delay(500);
        }  
        Serial.println("SensoreAttached");
    }

    
}
void BatteryLow()
{

    delay(200); // this delay is because in a moments relays get on use too many current and so battery voltage get decrease for a moment.
    if (GetBattery() <= 3.75)
    {
        Serial.println("BatteryLow");
        Serial.println(GetBattery());
        EEPROM.update(14, 0);
        u8g2.clearBuffer();
        u8g2.setFont(u8g2_font_battery19_tn);
        u8g2.drawGlyph(60, 26, BTStatus);
        u8g2.sendBuffer();
        digitalWrite(Heater, LOW);
        digitalWrite(Cooler, LOW);
        
        bool al = 0;
        while (GetBattery() <= 3.7)
        {
            delay(1000);
            digitalWrite(Buzzer,al);
            al != al;
        }
    }
    Serial.println("BatteryOK");
}
float GetBattery()
{
    long result;
    // Read 1.1V reference against AVcc
    ADMUX = _BV(REFS0) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
    delay(2);            // Wait for Vref to settle
    ADCSRA |= _BV(ADSC); // Convert
    while (bit_is_set(ADCSRA, ADSC));
    result = ADCL;
    result |= ADCH << 8;
    result = 1126400L / result; // Back-calculate AVcc in mV
    float Voltage = (float)result / 1000;//Converting mV to V
    Voltage += Voltage * 0.1;//there is a problem in reading VCC that resalt is 90% of Real VCC.
    if (Voltage >= 4.2)
    {
        BTStatus = 53;
    }
    else if (Voltage >= 4.0)
    {
        BTStatus = 52;
    }
    else if (Voltage >= 3.9)
    {
        BTStatus = 51;
    }
    else if (Voltage >= 3.8)
    {
        BTStatus = 49;
    }
    else
    {
        BTStatus = 48;
    }
    return Voltage;
}
void Setting()
{
    TempSensors.requestTemperatures();
    Temp1 = TempSensors.getTempCByIndex(0);
    if(Temp1<=-126){
        InsertSensor();
    }
    u8g2.clearBuffer();
    char MaxStr[7];
    char MinStr[7];
    getMaxMin(MaxStr, MinStr);
    u8g2.setFont(u8g2_font_profont12_tr);
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
    { // MaxTemp
        int VolumeV = (analogRead(Volume) / 4) - 131;
        if (VolumeV - 1 > MinTemp)
        {
            MaxTemp = VolumeV;
        }
        u8g2.drawRFrame(1, 1, width + 1, 15, 1);
        // Drawing Frame
    }
    else if (Item == 1)
    { // MinTemp
        int VolumeV = (analogRead(Volume) / 4) - 131;
        if(VolumeV<-50){
          VolumeV = -50;
        }
        if (VolumeV + 1 < MaxTemp)
        {
            MinTemp = VolumeV;
        }
        u8g2.drawRFrame(1, 19, width + 1, 15, 1);
    }
    else if (Item == 2)
    { // Alarm
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
    { // Heater
        u8g2.drawRFrame(width + 30, 5, 22, 22, 1);
        if (digitalRead(ChangeSW) == 1)
        {
            delay(40);
            if (digitalRead(ChangeSW) == 1)
            {
                if (HeaterState == 1)
                {
                    HeaterState = 0;
                    digitalWrite(Heater, LOW);
                }
                else
                {
                    HeaterState = 1;
                }
                delay(160);
            }
        }
    }
    else if (Item == 4)
    { // Cooler
        u8g2.drawRFrame(width + 51, 5, 22, 22, 1);
        if (digitalRead(ChangeSW) == 1)
        {
            delay(40);
            if (digitalRead(ChangeSW) == 1)
            {
                if (CoolerState == 1)
                {
                    CoolerState = 0;
                    digitalWrite(Cooler, LOW);
                }
                else
                {
                    CoolerState = 1;
                }
                delay(160);
            }
        }
    }

    // Drawing Icons
    u8g2.setFont(u8g2_font_open_iconic_play_2x_t);

    width += 5;
    if (Alarm == 1)
    {
        u8g2.drawGlyph(width + 4, 24, 79);
    }
    else
    {
        u8g2.drawGlyph(width + 4, 24, 81);
    }
    u8g2.setFont(u8g2_font_open_iconic_weather_2x_t);
    if (HeaterState == 1)
    {
        u8g2.drawGlyph(width + 28, 24, 69);
    }
    else
    {
        u8g2.drawGlyph(width + 28, 24, 66);
    }
    u8g2.setFont(u8g2_font_open_iconic_check_2x_t);
    if (CoolerState == 1)
    {
        u8g2.setFont(u8g2_font_open_iconic_arrow_2x_t);
        u8g2.drawGlyph(width + 50, 24, 87);
    }
    else
    {
        u8g2.drawGlyph(width + 50, 24, 66);
    }
    ApplyOuts();

    if (Item == 5)
    {
        WriteEEPROM();
        Place = 0;
        Item = 0;
        u8g2.clearBuffer();
        u8g2.setFont(u8g2_font_open_iconic_check_2x_t);
        u8g2.drawGlyph(56, 24, 65);
        delay(400);
    }
    u8g2.sendBuffer();
}

void MainSC()
{
    TempSensors.requestTemperatures();
    Temp1 = TempSensors.getTempCByIndex(0);
    if(Temp1<=-126){
        InsertSensor();
    }
    u8g2.clearBuffer();
    u8g2.setFont(u8g2_font_logisoso18_tr);

    char str[7];
    getString(str);
    int width_temp = u8g2.getStrWidth(str);
    u8g2.drawStr(1, 30, str);
    u8g2.setFont(u8g2_font_profont12_tr);
    u8g2.drawUTF8(width_temp + 4, 32, "°C");

    char Max[7];
    char Min[7];
    getMaxMin(Max, Min);
    u8g2.drawStr(width_temp + 34, 10, Max);
    u8g2.drawStr(width_temp + 34, 32, Min);
    u8g2.setFont(u8g2_font_open_iconic_arrow_1x_t);

    u8g2.drawGlyph(width_temp + 24, 10, 75); // Max
    u8g2.drawGlyph(width_temp + 24, 31, 72); // Min

    u8g2.setFont(u8g2_font_open_iconic_play_1x_t);
    ApplyOuts();
    // Drawing icons

    if (Alarm == 1)
    {
        u8g2.drawGlyph(4, 9, 79); // Sound
    }
    else
    {
        u8g2.drawGlyph(4, 9, 81);
    }
    u8g2.setFont(u8g2_font_open_iconic_weather_1x_t);
    if (HeaterState == 1)
    {
        u8g2.drawGlyph(16, 9, 69);
    }
    else
    {
        u8g2.drawGlyph(16, 9, 66);
    }
    u8g2.setFont(u8g2_font_open_iconic_arrow_1x_t);
    if (CoolerState == 1)
    {
        u8g2.drawGlyph(28, 9, 87);
    }
    else
    {
        u8g2.setFont(u8g2_font_open_iconic_check_1x_t);
        u8g2.drawGlyph(28, 9, 66);
    }
    u8g2.drawGlyph(40, 9, Status);
    u8g2.setFont(u8g2_font_battery19_tn);
    u8g2.drawGlyph(55, 19, BTStatus);
    u8g2.sendBuffer();
}

void WriteEEPROM()
{
    EEPROM.put(AdMax, MaxTemp);
    EEPROM.put(AdMin, MinTemp);
    EEPROM.put(AdAlarm, Alarm);

    EEPROM.put(AdHS, HeaterState);
    EEPROM.put(AdCS, CoolerState);
    Serial.println("SettingUpdate");
}

void ApplyOuts()
{

    if (Temp1 >= MaxTemp)
    { // temprature is higher than max value
        Status = 68;
        digitalWrite(Buzzer, Alarm);
        digitalWrite(Cooler, CoolerState);
        digitalWrite(Heater, LOW);
        Serial.println("HT");
    }
    else if (Temp1 <= MinTemp)
    { // temprature is lower than min value
        Status = 71;
        digitalWrite(Buzzer, Alarm);
        digitalWrite(Heater, HeaterState);
        digitalWrite(Cooler, LOW);
        Serial.println("LT");
    }
    else if (Temp1 > MaxTemp - ((MaxTemp - MinTemp) / 3))
    { // this means starting cooling when temp is more than 2/3 avrage max-min
        Status = 84;
        digitalWrite(Cooler, CoolerState);
        digitalWrite(Heater, LOW);
        digitalWrite(Buzzer, LOW);
        Serial.println("HPT");
    }
    else if (Temp1 < MinTemp + ((MaxTemp - MinTemp) / 3))
    {// this means starting cooling when temp is less than 1/3 avrage max-min
        Status = 85;
        digitalWrite(Heater, HeaterState);
        digitalWrite(Cooler, LOW);
        digitalWrite(Buzzer, LOW);
        Serial.println("LPT");
    }

    else
    {
        float temp = TempLog[0];
        for (int i = 0; i < 7; i++)
            TempLog[i] = TempLog[i + 1];
        TempLog[7] = temp;
        if (((TempLog[0] + TempLog[1] + TempLog[2] + TempLog[3]) - (TempLog[4] + TempLog[5] + TempLog[6] + TempLog[7])) > 0 and Temp1 < (MaxTemp - MinTemp) / 2)
        { // Ro be kahesh
            if (HeaterState == 1)
            {
                digitalWrite(Heater, HIGH);
                digitalWrite(Cooler, LOW);
                Serial.println("FDT");
            }
        }
        else if (((TempLog[0] + TempLog[1] + TempLog[2] + TempLog[3]) - (TempLog[4] + TempLog[5] + TempLog[6] + TempLog[7])) < 0 and Temp1 > (MaxTemp - MinTemp) / 2)
        { // Ro be AfZayesh
            if (CoolerState == 1)
            {
                digitalWrite(Cooler, HIGH);
                digitalWrite(Heater, LOW);
                Serial.println("FIT");
            }
        }
        else
        {
            digitalWrite(Buzzer, LOW);
            digitalWrite(Cooler, LOW);
            digitalWrite(Heater, LOW);
        }
        Status = 91;
    }
}
