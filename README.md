# digital_thermostat
this project is a Digital Thermostat with arduino nano and SSD1306 128x32 Oled display with DS18B20 Temprature sensor.
this project works with 3.7 li-ion battery and relays can work together.anyway you can use usb charger or adaptor for powering up device.
also you can control your board with serial comminication or USB cable and desktop application.
PCB is ready and you can make it in 1 Layer.
## Board
![board](https://user-images.githubusercontent.com/74818141/152884199-2d8fc2fc-ba44-4fd1-bc2b-f0659257e77f.png)

![IMG_20220123_230904](https://user-images.githubusercontent.com/74818141/152884563-82017bb8-dfe3-4def-8524-422b30b4160e.jpg)

-**In top-right you can change Relays source with jumpers between battery and adaptor jack**

-**You can choose the regulator based on the voltage of your relays**

-**If the relays are connected to the battery voltage source
Replace regulator َU1 with 15 ohm SMD resistor**

_**Remember Serial Comminication is for 3.3V so when you run your board with battery if your bluetooth madule had resistor in RX pin it filter your comminication.
best way is using bluetooth madules without boards or shorting RX in resistor**

## Serial Comminication
### board sends us this messages.
Prefix| Message | Description |
--- | --- | --- |
SN+| SettingUp | First Message when device turned on |
SN+| FirstStart | Board never used before |
SN+| Ready | Setup complite and ready to work |
SN+| SensorDetached | DS18B20 is not available |
SN+| SensorAttached | when sensor problem solved |
SN+| BatteryLow | Battery voltage is less than 3.75V and device not works |
SN+| BatteryOK | After connecting the charger and increasing the battery voltage to 3.75 volts |
SN+| SettingUpdate | When making changes to settings |
SN+| HT | Temperature is more than maximum temperature |
SN+| LT | Temperature is less than minimum temperature |
SN+| HPT | Temperature is more than (2/3 Avrage minimum and maximum) |
SN+| LPT | Temperature is less than (1/3 Avrage minimum and maximum) |
SN+| FIT | The temperature rises rapidly |
SN+| FDT | The temperature drops rapidly |
SN+| Normal | Temprature is normal |
SN+| {float} | Temprature value |

-**SN :To identify the message center (prevents interference if multiple boards are used)**

-**All messages are sent only once and are not repeated.If the temperature does not change, a new temperature message will not be sent**
### Getting information from board:
#### Commands:

 Command | response |
 --- | --- |
Get+ | SN+Temp+MinTemp+MaxTemp+AlarmEnable+HeaterEnable+CoolerEnable+VccVoltage+PowerSavingMode|
Get+T+ | SN+Temp |

Command | response |
 --- | --- |
 Set+MaxTemp+MinTemp+AlarmEnable+HeaterEnable+CoolerEnable+PowerSavingMode | SettingUpdate
  
  -If you do not want to change the numerical values, replace it with 200 and for logical values, replace it with 2 

## Desktop Application

![psc1](https://user-images.githubusercontent.com/74818141/152890608-c4c60786-44ff-4c4e-bedf-fe8d783c2551.png)

writed with python with Qt5 can be used in Linux and Windows
