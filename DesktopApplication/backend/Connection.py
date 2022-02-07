
import serial
import glob
import sys
import bluetooth
import time

data_dict = {
    "SN": 0,
    "Temp": 0,
    "MaxTemp": 0,
    "MinTemp": 0,
    "Alarm": 0,
    "Heater": 0,
    "Cooler": 0,
    "BatteryVoltage": 0,
    "PowerSavingMode": 0
}
class Connection:
    def __init__(self,Connection):
        self.Connection = Connection

class SerialPort():
    def __init__(self,port:str,baundrate=9600,time_out=1,Name=""):
        self.port = port
        self.baundrate = baundrate
        self.time_out = time_out
        self.name = ""
        self._connection = None
        self._isConnected = False
        self.LastGet = {}
    def Connect(self):
        try:
            self._connection = serial.Serial(self.port,self.baundrate)
        except:
            return "Connection Fail!!!"
        else:
            self._isConnected = True
            return "Connected"
    
    def Disconnect(self):
        try:
            self._connection.close()
        except:
            return "Disconnection Fail!!!"
        else:
            self._isConnected = False
            return "Disconnected"

    def CheckConnection(self)->bool:
        self._isConnected = self._connection.isOpen()
        return self._isConnected

    def GetCommandMessage(self,MaxTemp=200,MinTemp=200,AlarmState=2,HeaterState=2,CoolerState=2,PowerSavingMode=2):
        return bytes(f"Set+{MaxTemp}+{MinTemp}+{AlarmState}+{HeaterState}+{CoolerState}+{PowerSavingMode}","utf-8")
 

    def SendCommand(self,MaxTemp=200,MinTemp=200,AlarmState=2,HeaterState=2,CoolerState=2,PowerSavingMode=2):
        if self.CheckConnection():
            try:
                self._connection.write(bytes(f"Set+{MaxTemp}+{MinTemp}+{AlarmState}+{HeaterState}+{CoolerState}+{PowerSavingMode}","utf-8"))
            except:
                return False
            else:
                return True
        else:
            return False
    def Get(self,Trys = 4):
        if self.CheckConnection():
            self._connection.write(b"Get+")
            my_data = ""
            Trying = Trys
            while True:
                DATA = self._connection.readline()
                DATA = str(DATA,"utf-8")
                DATA = DATA.rstrip()
                data_list = DATA.split("+")
                if data_list[0].isdigit():
                    my_data = DATA
                    break
                else:
                    Trying -= 1
                    self._connection.write(b"Get+")
                    if Trying == 0:
                        break
                time.sleep(0.2)
                    
            return my_data

    def GetTemprature(self):
        if self.CheckConnection():
            self._connection.write(b"Get+T+")
            my_data = None
            Trying = 4  
            while True:
                try:
                    DATA = self._connection.readline()
                    DATA = str(DATA,"utf-8")
                    data_list = DATA.split("+")
                    if len(data_list)>1:
                        try:
                            my_data = float(data_list[1])
                        except:pass
                        else:return my_data
                    else:
                        Trying -= 1
                        if Trying == 0:
                            break
                    time.sleep(0.2)
                    return float(my_data[1])
                except:return None



def SearchSerialports()->dict:
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = dict()
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result[s.name]=s.get_settings()

        except (OSError, serial.SerialException):
            pass
    return result
def SearchBluetooths():
    nearby_devices =bluetooth.discover_devices(lookup_names = True)
    return nearby_devices