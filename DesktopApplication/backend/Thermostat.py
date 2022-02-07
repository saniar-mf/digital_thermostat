class Thermostat():
    def __init__(self,SN,Temp=0.0,MaxTemp=30.0,MinTemp=20.0,Alarm=1,Heater=1,Cooler=1,PowerSaving=0,BatteryVoltage=4.2,BatteryCapacity=4500):
        self.Temp = Temp
        self.MaxTemp = MaxTemp
        self.MinTemp = MinTemp
        self.Alarm = Alarm
        self.Heater = Heater
        self.Cooler = Cooler
        #0 = disabled - 1 = Enable/NotWorking - 2 = Working
        self.HeaterState = 0
        self.CoolerState = 0
        self.AlarmState = 0
        self.PowerSaving = PowerSaving
        self.SN = SN

        self.BatteryVoltage = BatteryVoltage
        self.Status = "Normal"
        self.BatteryCapacity = BatteryCapacity
    def SetViaAlgoritm(self):
        if (self.Temp >= self.MaxTemp):
            if self.Alarm:self.AlarmState = 2
            else:self.AlarmState = 0
            if self.Cooler:self.CoolerState = 2
            else:self.CoolerState = 0
            if self.Heater:self.HeaterState = 1
            else:self.HeaterState = 0
            self.Status = "HT"

        elif (self.Temp <= self.MinTemp):
            if self.Alarm:self.AlarmState = 2
            else:self.AlarmState = 0
            if self.Cooler:self.CoolerState = 1
            else:self.CoolerState = 0
            if self.Heater:self.HeaterState = 2
            else:self.HeaterState = 0
            self.Status = "LT"
        elif (self.Temp > self.MaxTemp - ((self.MaxTemp - self.MinTemp) / 3)):
            if self.Alarm:self.AlarmState = 1
            else:self.AlarmState = 0
            if self.Cooler:self.CoolerState = 2
            else:self.CoolerState = 0
            if self.Heater:self.HeaterState = 1
            else:self.HeaterState = 0
            self.Status = "HPT"
        elif (self.Temp < self.MinTemp + ((self.MaxTemp - self.MinTemp) / 3)):
            if self.Alarm:self.AlarmState = 1
            else:self.AlarmState = 0
            if self.Cooler:self.CoolerState = 1
            else:self.CoolerState = 0
            if self.Heater:self.HeaterState = 2
            else:self.HeaterState = 0
            self.Status = "LPT"
        
        else:
            if self.Alarm:self.AlarmState = 1
            else:self.AlarmState = 0
            if self.Cooler:self.CoolerState = 1
            else:self.CoolerState = 0
            if self.Heater:self.HeaterState = 1
            else:self.HeaterState = 0
            self.Status = "Normal"

    def SetViaStatus(self,status:str):
        if status == "HT":
            if self.Alarm:self.AlarmState = 2
            else:self.AlarmState = 0
            if self.Cooler:self.CoolerState = 2
            else:self.CoolerState = 0
            if self.Heater:self.HeaterState = 1
            else:self.HeaterState = 0
            self.Status = "HT"

        elif status == "LT":
            if self.Alarm:self.AlarmState = 2
            else:self.AlarmState = 0
            if self.Cooler:self.CoolerState = 1
            else:self.CoolerState = 0
            if self.Heater:self.HeaterState = 2
            else:self.HeaterState = 0
            self.Status = "LT"

        elif status == "HPT":
            if self.Alarm:self.AlarmState = 1
            else:self.AlarmState = 0
            if self.Cooler:self.CoolerState = 2
            else:self.CoolerState = 0
            if self.Heater:self.HeaterState = 1
            else:self.HeaterState = 0
            self.Status = "HPT"

        elif status == "LPT":
            if self.Alarm:self.AlarmState = 1
            else:self.AlarmState = 0
            if self.Cooler:self.CoolerState = 1
            else:self.CoolerState = 0
            if self.Heater:self.HeaterState = 2
            else:self.HeaterState = 0
            self.Status = "LPT"

        elif status == "LPT":
            if self.Alarm:self.AlarmState = 1
            else:self.AlarmState = 0
            if self.Cooler:self.CoolerState = 1
            else:self.CoolerState = 0
            if self.Heater:self.HeaterState = 2
            else:self.HeaterState = 0
            self.Status = "LPT"

        elif status == "FDT":
            if self.Alarm:self.AlarmState = 1
            else:self.AlarmState = 0
            if self.Cooler:self.CoolerState = 1
            else:self.CoolerState = 0
            if self.Heater:self.HeaterState = 2
            else:self.HeaterState = 0
            self.Status = "FDT"

        elif status == "FIT":
            if self.Alarm:self.AlarmState = 1
            else:self.AlarmState = 0
            if self.Cooler:self.CoolerState = 2
            else:self.CoolerState = 0
            if self.Heater:self.HeaterState = 1
            else:self.HeaterState = 0
            self.Status = "FIT"

        elif status == "Normal":
            if self.Alarm:self.AlarmState = 1
            else:self.AlarmState = 0
            if self.Cooler:self.CoolerState = 1
            else:self.CoolerState = 0
            if self.Heater:self.HeaterState = 1
            else:self.HeaterState = 0
            self.Status = "Normal"


    def UpdateFromString(self,RecivedString:str):
        def IsFloat(val):
            try:float(val)
            except:return False
            else:return True
        #SN+Temp+MinTemp+MaxTemp+AlarmState+HeaterState+CoolerState+VccVoltage+PowerSavingMode
        infos_list = RecivedString.split("+")
        for i in range(len(infos_list)):
            try:
                if i == 0 and IsFloat(infos_list[i]):
                    self.SN = int(infos_list[i])
                
                if i == 1 and IsFloat(infos_list[i]):
                    self.Temp = float(infos_list[i])  

                if i == 2 and IsFloat(infos_list[i]):
                    self.MaxTemp = float(infos_list[i])  
                if i == 3 and IsFloat(infos_list[i]):
                    self.MinTemp = float(infos_list[i])  
                if i == 4 and IsFloat(infos_list[i]):
                    self.Alarm = int(infos_list[i])  
                if i == 5 and IsFloat(infos_list[i]):
                    self.Heater = int(infos_list[i])  
                if i == 6 and IsFloat(infos_list[i]):
                    self.Cooler = int(infos_list[i])  
                if i == 7 and IsFloat(infos_list[i]):
                    self.BatteryVoltage = float(infos_list[i])  
                if i == 8 and IsFloat(infos_list[i]):
                    self.PowerSaving = int(infos_list[i])  
            except:pass 
