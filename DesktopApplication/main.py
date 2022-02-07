# -*- coding: utf-8 -*-


from PyQt5 import QtCore, QtGui, QtWidgets
from backend import Thermostat, Connection
from ui import ConnectionDialog
import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
ICONS_DIR = os.path.join(BASE_DIR, "ui/img/")

MessageList = []

def GetMessage():
    global MessageList
    if len(MessageList) >0:
        mainmessage = MessageList[0]
        MessageList.pop(0)
        return mainmessage
    else:return None

def AddMessage(message:bytes):
    global MessageList
    MessageList.append(message)
    MessageList = list(set(MessageList))

def IsFloat(msg:str):
    try:float(msg)
    except:return False
    else:return True

class MessageSender(QtCore.QThread):
    signal = QtCore.pyqtSignal(bool)
    def __init__(self, parent = None ) -> None:
        QtCore.QThread.__init__(self, parent)
        self.connection = None

    def run(self):
        while True:
            global MessageList
            if len(MessageList):
                CM = GetMessage()
                self.connection._connection.write(CM)
                self.signal.emit(True)


class MessageHandler(QtCore.QThread):
    signal = QtCore.pyqtSignal(dict)

    def __init__(self, parent = None ) -> None:
        QtCore.QThread.__init__(self, parent)
        self.delay = 0
        self.SN = 0
        self.messages = ["SettingUp","FirstStart","Ready","SensorDetached","SensorAttached","BatteryLow","BatteryOK","SettingUpdate","HT","LT","HPT","LPT","FDT","FIT","Normal"]
        self.GetInfoAfterSicle = 20
        self._currentSicle = 0
        self.ReadTemp = False
        self.TempCicle = 3
        self.connection = None

    def run(self):
        while True:
            if not self.connection.CheckConnection():
                self.signal.emit({"Error":"Disconnected"})
                break
            message = b""
            try:
                message = self.connection._connection.readline()
            except Exception as e:
                print(e)
                self.signal.emit({"Error":"Disconnected"})
                break
            if message:
                try:#this try is for encoding errors.
                    message = str(message,"utf-8")
                    for r in ["b'","'","\r","\n"]:
                        message = message.replace(r,"")
                    message = message.rstrip()
                    _messages = message.split("+")

                    if _messages[0].isdigit() and (int(_messages[0]) == self.SN or self.SN == 0) and len(_messages)>1:
                        if _messages[1] in self.messages:
                            self.signal.emit({"Message":message})
                        else:
                            if len(_messages) == 2 and IsFloat(_messages[1]):#is Temprature
                                self.signal.emit({"Temp":float(_messages[1])})
                            else:
                                self.signal.emit({"Info":message})
                except:pass
            self._currentSicle += 1
            if self._currentSicle == self.GetInfoAfterSicle:
                AddMessage(b"Get+")
                self._currentSicle = 0
            else:self._currentSicle = 20
            if self.ReadTemp and self.TempCicle >0:
                self.TempCicle = self.TempCicle -1
                AddMessage(b"Get+T+")
            else:self.TempCicle = 3


class Ui_MainWindow(object):
    BatteryImages = {
        "0":"BatteryLow.png",
        "1":"BT_1.png",
        "2":"BT_2.png",
        "3":"BT_3.png",
        "4":"BT_4.png",
        "5":"BT_1.png",
        "F":"BT_Charching.png"
    }
    TempFrameStyles = {
        "Normal":"""QFrame#TempFrame{
	background-color: rgba(10, 10, 0, 10);
	border-radius:10px;
	color:white;
}""",
        "HT":"""QFrame#TempFrame{
	background-color: rgba(255, 39, 43, 150);
	border-radius:10px;
	color:white;
}""",
        "LT":"""QFrame#TempFrame{
	background-color: rgba(154, 65, 255, 150);
	border-radius:10px;
	color:white;
}""",
        "HPT":"""QFrame#TempFrame{
	background-color: qlineargradient(spread:reflect, x1:0, y1:1, x2:0, y2:0, stop:0 rgba(6, 118, 116, 125), stop:1 rgba(255, 128, 195, 209));
	border-radius:10px;
	color:white;            
}""",
        "LPT":"""QFrame#TempFrame{
	background-color: qlineargradient(spread:reflect, x1:0, y1:1, x2:0, y2:0, stop:0 rgba(6, 118, 116, 125), stop:1 rgba(150, 128, 255, 209));
	border-radius:10px;
	color:white;
}""",
        "FDT":"""QFrame#TempFrame{
	background-color: rgba(200, 150, 255, 150);
	border-radius:10px;
	color:white;
}""",
        "FIT":"""QFrame#TempFrame{
	background-color: rgba(255, 120, 43, 150);
	border-radius:10px;
	color:white;
}"""
    }
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setMinimumSize(QtCore.QSize(800, 600))
        MainWindow.setMaximumSize(QtCore.QSize(800, 600))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(ICONS_DIR, "logo.png")),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        MainWindow.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.shadow = QtWidgets.QGraphicsDropShadowEffect(MainWindow)
        qr = MainWindow.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        MainWindow.move(qr.topLeft())
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QtGui.QColor(0,0,0,60))
        
        self.AditionalDialog = QtWidgets.QDialog()
        self.ConnectionDialog = ConnectionDialog.Ui_Dialog()
        self.ConnectionDialog.setupUi(self.AditionalDialog)
        self.HeaterOn = QtGui.QMovie(os.path.join(ICONS_DIR, "HeaterWorking.gif"))
        self.HeaterOff = QtGui.QPixmap(os.path.join(ICONS_DIR, "Heater.png"))
        self.CoolerOn = QtGui.QMovie(os.path.join(ICONS_DIR, "FanWorking.gif"))
        self.CoolerOff = QtGui.QPixmap(os.path.join(ICONS_DIR, "fan.png"))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.MainFrame = QtWidgets.QFrame(self.centralwidget)
        self.MainFrame.setStyleSheet("""QFrame#MainFrame{
                                         background-color: rgba(48, 153, 185, 200);
                                         border-radius:10px;
                                     }""")
        self.MainFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.MainFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.MainFrame.setObjectName("MainFrame")
        self.MainFrame.setGraphicsEffect(self.shadow)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.MainFrame)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.TempFrame = QtWidgets.QFrame(self.MainFrame)
        self.TempFrame.setStyleSheet("QFrame#TempFrame{\n"
                                     "    background-color: rgba(10, 10, 0, 10);\n"
                                     "    border-radius:10px;\n"
                                     "    color:white;\n"
                                     "}")
        self.TempFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.TempFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.TempFrame.setObjectName("TempFrame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.TempFrame)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.GB_MinTemp = QtWidgets.QGroupBox(self.TempFrame)
        self.GB_MinTemp.setMinimumSize(QtCore.QSize(200, 210))
        self.GB_MinTemp.setMaximumSize(QtCore.QSize(200, 210))
        font = QtGui.QFont()
        font.setFamily("URW Gothic [urw]")
        font.setPointSize(12)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.GB_MinTemp.setFont(font)
        self.GB_MinTemp.setStyleSheet("QGroupBox#GB_MinTemp{\n"
                                      "    background-color: rgba(0, 0, 0, 10);\n"
                                      "    border-radius:10px;\n"
                                      "    color:white;\n"
                                      "}")
        self.GB_MinTemp.setObjectName("GB_MinTemp")
        self.MinTemp = QtWidgets.QDial(self.GB_MinTemp)
        self.MinTemp.setGeometry(QtCore.QRect(0, 50, 201, 161))
        self.MinTemp.setCursor(QtGui.QCursor(QtCore.Qt.SplitHCursor))
        self.MinTemp.setAutoFillBackground(False)
        self.MinTemp.setStyleSheet("background-color: qconicalgradient(cx:0.5, cy:0.5, angle:0, stop:0 rgba(255, 0, 0, 255), stop:0.186275 rgba(0, 217, 52, 255), stop:0.352941 rgba(0, 217, 197, 255), stop:0.52451 rgba(0, 0, 255, 255), stop:0.622549 rgba(0, 0, 255, 255), stop:0.857843 rgba(255, 0, 0, 255));\n"
                                   "")
        self.MinTemp.setMinimum(-50)
        self.MinTemp.setMaximum(125)
        self.MinTemp.setPageStep(1)
        self.MinTemp.setSingleStep(1)
        self.MinTemp.setValue(-49)
        self.MinTemp.setInvertedAppearance(False)
        self.MinTemp.setObjectName("MinTemp")
        self.LB_MinTemp = QtWidgets.QLabel(self.GB_MinTemp)
        self.LB_MinTemp.setGeometry(QtCore.QRect(60, 120, 80, 40))
        font = QtGui.QFont()
        font.setFamily("URW Gothic [UKWN]")
        font.setPointSize(28)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.LB_MinTemp.setFont(font)
        self.LB_MinTemp.setObjectName("LB_MinTemp")
        self.horizontalLayout.addWidget(self.GB_MinTemp)
        self.TempMonitor = QtWidgets.QLCDNumber(self.TempFrame)
        self.TempMonitor.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.TempMonitor.setSmallDecimalPoint(True)
        self.TempMonitor.setDigitCount(4)
        self.TempMonitor.setProperty("intValue", 0)
        self.TempMonitor.setObjectName("TempMonitor")
        self.horizontalLayout.addWidget(self.TempMonitor)
        self.TempLable = QtWidgets.QLabel(self.TempFrame)
        self.TempLable.setMaximumSize(QtCore.QSize(100, 200))
        font = QtGui.QFont()
        font.setFamily("Noto Sans Adlam")
        font.setPointSize(48)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.TempLable.setFont(font)
        self.TempLable.setLocale(QtCore.QLocale(
            QtCore.QLocale.English, QtCore.QLocale.AmericanSamoa))
        self.TempLable.setObjectName("TempLable")
        self.horizontalLayout.addWidget(self.TempLable)
        self.GB_MaxTemp = QtWidgets.QGroupBox(self.TempFrame)
        self.GB_MaxTemp.setMinimumSize(QtCore.QSize(200, 210))
        self.GB_MaxTemp.setMaximumSize(QtCore.QSize(200, 210))
        font = QtGui.QFont()
        font.setFamily("URW Gothic [urw]")
        font.setPointSize(12)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.GB_MaxTemp.setFont(font)
        self.GB_MaxTemp.setStyleSheet("QGroupBox#GB_MaxTemp{\n"
                                      "    background-color: rgba(0, 0, 0, 10);\n"
                                      "    border-radius:10px;\n"
                                      "    color:white;\n"
                                      "}")
        self.GB_MaxTemp.setObjectName("GB_MaxTemp")
        self.MaxTemp = QtWidgets.QDial(self.GB_MaxTemp)
        self.MaxTemp.setGeometry(QtCore.QRect(0, 50, 201, 161))
        self.MaxTemp.setCursor(QtGui.QCursor(QtCore.Qt.SplitHCursor))
        self.MaxTemp.setAutoFillBackground(False)
        self.MaxTemp.setStyleSheet("background-color: qconicalgradient(cx:0.5, cy:0.5, angle:0, stop:0 rgba(255, 0, 0, 255), stop:0.186275 rgba(0, 217, 52, 255), stop:0.352941 rgba(0, 217, 197, 255), stop:0.52451 rgba(0, 0, 255, 255), stop:0.622549 rgba(0, 0, 255, 255), stop:0.857843 rgba(255, 0, 0, 255));\n"
                                   "")
        self.MaxTemp.setMinimum(-125)
        self.MaxTemp.setMaximum(50)
        self.MaxTemp.setValue(-120)
        self.MaxTemp.setPageStep(1)
        self.MaxTemp.setSingleStep(1)
        self.MaxTemp.setInvertedAppearance(True)
        self.MaxTemp.setObjectName("MaxTemp")
        self.LB_MaxTemp = QtWidgets.QLabel(self.GB_MaxTemp)
        self.LB_MaxTemp.setGeometry(QtCore.QRect(60, 120, 80, 40))
        font = QtGui.QFont()
        font.setFamily("URW Gothic [UKWN]")
        font.setPointSize(28)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.LB_MaxTemp.setFont(font)
        self.LB_MaxTemp.setObjectName("LB_MaxTemp")
        self.horizontalLayout.addWidget(self.GB_MaxTemp)
        self.verticalLayout_2.addWidget(self.TempFrame)
        self.BTN_Frame = QtWidgets.QFrame(self.MainFrame)
        self.BTN_Frame.setEnabled(True)
        self.BTN_Frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.BTN_Frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.BTN_Frame.setObjectName("BTN_Frame")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.BTN_Frame)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.PB_Clear = QtWidgets.QPushButton(self.BTN_Frame)
        self.PB_Clear.setMinimumSize(QtCore.QSize(150, 50))
        self.PB_Clear.setMaximumSize(QtCore.QSize(150, 50))
        font = QtGui.QFont()
        font.setFamily("Bitstream Charter")
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.PB_Clear.setFont(font)
        self.PB_Clear.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.PB_Clear.setStyleSheet("background-color: rgba(38, 15, 29, 150);\n"
                                    "color: rgb(250, 250, 250);\n"
                                    "border-radius:10px;")
        self.PB_Clear.setObjectName("PB_Clear")
        self.horizontalLayout_2.addWidget(self.PB_Clear)
        self.PB_Save = QtWidgets.QPushButton(self.BTN_Frame)
        self.PB_Save.setMinimumSize(QtCore.QSize(150, 50))
        self.PB_Save.setMaximumSize(QtCore.QSize(150, 50))
        font = QtGui.QFont()
        font.setFamily("Bitstream Charter")
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.PB_Save.setFont(font)
        self.PB_Save.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.PB_Save.setStyleSheet("background-color: rgb(37, 157, 67);\n"
                                   "color: rgb(250, 250, 250);\n"
                                   "border-radius:10px;")
        self.PB_Save.setObjectName("PB_Save")
        self.horizontalLayout_2.addWidget(self.PB_Save)
        self.verticalLayout_2.addWidget(self.BTN_Frame)
        self.tabWidget = QtWidgets.QTabWidget(self.MainFrame)
        self.tabWidget.setStyleSheet("QTabWidget#tabWidget{\n"
                                     "    background-color: rgba(0, 0, 0, 50);\n"
                                     "    border-radius:10px;\n"
                                     "    alternate-background-color: rgb(60, 0, 255);\n"
                                     "}")
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.South)
        self.tabWidget.setObjectName("tabWidget")
        self.setting = QtWidgets.QWidget()
        self.setting.setObjectName("setting")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.setting)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.Fr_Battery = QtWidgets.QFrame(self.setting)
        self.Fr_Battery.setMinimumSize(QtCore.QSize(95, 200))
        self.Fr_Battery.setMaximumSize(QtCore.QSize(95, 200))
        self.Fr_Battery.setStyleSheet("QFrame#Fr_Battery{\n"
                                      "    background-color: rgba(50, 200, 0, 100);\n"
                                      "    border-radius:10px;\n"
                                      "    color:white;\n"
                                      "}")
        self.Fr_Battery.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.Fr_Battery.setFrameShadow(QtWidgets.QFrame.Raised)
        self.Fr_Battery.setObjectName("Fr_Battery")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.Fr_Battery)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.LB_BT = QtWidgets.QLabel(self.Fr_Battery)
        self.LB_BT.setMinimumSize(QtCore.QSize(75, 90))
        self.LB_BT.setSizeIncrement(QtCore.QSize(75, 90))
        self.LB_BT.setText("")
        self.LB_BT.setPixmap(QtGui.QPixmap(
            os.path.join(ICONS_DIR, "BT_4.png")))
        self.LB_BT.setScaledContents(True)
        self.LB_BT.setObjectName("LB_BT")
        self.verticalLayout_3.addWidget(self.LB_BT)
        self.LB_BatteryPers = QtWidgets.QLabel(self.Fr_Battery)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.LB_BatteryPers.setFont(font)
        self.LB_BatteryPers.setObjectName("LB_BatteryPers")
        self.verticalLayout_3.addWidget(self.LB_BatteryPers)
        self.LB_ChargeTime = QtWidgets.QLabel(self.Fr_Battery)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.LB_ChargeTime.setFont(font)
        self.LB_ChargeTime.setObjectName("LB_ChargeTime")
        self.verticalLayout_3.addWidget(self.LB_ChargeTime)
        self.horizontalLayout_3.addWidget(self.Fr_Battery)
        spacerItem = QtWidgets.QSpacerItem(
            100, 20, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.ILB_Cooler = QtWidgets.QLabel(self.setting)
        self.ILB_Cooler.setMinimumSize(QtCore.QSize(140, 140))
        self.ILB_Cooler.setMaximumSize(QtCore.QSize(140, 140))
        self.ILB_Cooler.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.ILB_Cooler.setStyleSheet("QLabel{\n"
                                      "    background-color: rgba(50, 60, 50, 200);\n"
                                      "        border-radius:70px;\n"
                                      "border:4px solid rgba(100,100,100,250);\n"
                                      "}\n"
                                      "QLabel::hover{\n"
                                      "    background-color: rgba(100, 100, 200, 100);\n"
                                      "    border:0px solid rgba(100,100,100,150);\n"
                                      "        border-radius:70px;\n"
                                      "}")
        self.ILB_Cooler.setText("")
        self.ILB_Cooler.setPixmap(QtGui.QPixmap(
            os.path.join(ICONS_DIR, "fan.png")))
        self.ILB_Cooler.setScaledContents(True)
        self.ILB_Cooler.setObjectName("ILB_Cooler")
        self.horizontalLayout_3.addWidget(self.ILB_Cooler)
        spacerItem1 = QtWidgets.QSpacerItem(
            10, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.ILB_Sound = QtWidgets.QLabel(self.setting)
        self.ILB_Sound.setMinimumSize(QtCore.QSize(150, 150))
        self.ILB_Sound.setMaximumSize(QtCore.QSize(150, 150))
        self.ILB_Sound.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.ILB_Sound.setStyleSheet("QLabel{\n"
                                     "    background-color: rgba(50, 60, 50, 200);\n"
                                     "        border-radius:70px;\n"
                                     "border:4px solid rgba(100,100,100,250);\n"
                                     "}\n"
                                     "QLabel::hover{\n"
                                     "    background-color: rgba(100, 100, 200, 100);\n"
                                     "    border:0px solid rgba(100,100,100,150);\n"
                                     "        border-radius:70px;\n"
                                     "}")
        self.ILB_Sound.setText("")
        self.ILB_Sound.setPixmap(QtGui.QPixmap(os.path.join(ICONS_DIR, "sound_ok.png")))
        self.ILB_Sound.setScaledContents(True)
        self.ILB_Sound.setObjectName("ILB_Sound")
        self.horizontalLayout_3.addWidget(self.ILB_Sound)
        spacerItem2 = QtWidgets.QSpacerItem(
            10, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.ILB_Heater = QtWidgets.QLabel(self.setting)
        self.ILB_Heater.setMinimumSize(QtCore.QSize(140, 140))
        self.ILB_Heater.setMaximumSize(QtCore.QSize(140, 140))
        self.ILB_Heater.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.ILB_Heater.setStyleSheet("QLabel{\n"
                                      "    background-color: rgba(50, 60, 50, 200);\n"
                                      "        border-radius:70px;\n"
                                      "border:4px solid rgba(100,100,100,250);\n"
                                      "}\n"
                                      "QLabel::hover{\n"
                                      "    background-color: rgba(100, 100, 200, 100);\n"
                                      "    border:0px solid rgba(100,100,100,150);\n"
                                      "        border-radius:70px;\n"
                                      "}")
        self.ILB_Heater.setText("")
        self.ILB_Heater.setPixmap(QtGui.QPixmap(os.path.join(ICONS_DIR, "Heater.png")))
        self.ILB_Heater.setScaledContents(True)
        self.ILB_Heater.setObjectName("ILB_Heater")
        self.horizontalLayout_3.addWidget(self.ILB_Heater)
        spacerItem3 = QtWidgets.QSpacerItem(
            10, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem3)
        self.ILB_PowerSave = QtWidgets.QLabel(self.setting)
        self.ILB_PowerSave.setMinimumSize(QtCore.QSize(70, 70))
        self.ILB_PowerSave.setMaximumSize(QtCore.QSize(70, 70))
        self.ILB_PowerSave.setCursor(
            QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.ILB_PowerSave.setStyleSheet("QLabel{\n"
                                         "    background-color: rgba(200, 60, 50, 200);\n"
                                         "    border:0px solid rgba(100,100,100,150);\n"
                                         "        border-radius:35px;\n"
                                         "\n"
                                         "}\n"
                                         "QLabel::hover{\n"
                                         "\n"
                                         "    background-color: rgba(50, 60, 50, 200);\n"
                                         "        border-radius:35px;\n"
                                         "border:4px solid rgba(100,100,100,250);\n"
                                         "}")
        self.ILB_PowerSave.setText("")
        self.ILB_PowerSave.setPixmap(QtGui.QPixmap(
            os.path.join(ICONS_DIR, "lunarclient.png")))
        self.ILB_PowerSave.setScaledContents(True)
        self.ILB_PowerSave.setObjectName("ILB_PowerSave")
        self.horizontalLayout_3.addWidget(self.ILB_PowerSave)
        spacerItem4 = QtWidgets.QSpacerItem(
            100, 20, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem4)
        self.tabWidget.addTab(self.setting, "")
        self.Connection = QtWidgets.QWidget()
        self.Connection.setObjectName("Connection")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.Connection)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.ILB_StopConnection = QtWidgets.QLabel(self.Connection)
        self.ILB_StopConnection.setMinimumSize(QtCore.QSize(70, 70))
        self.ILB_StopConnection.setMaximumSize(QtCore.QSize(70, 70))
        self.ILB_StopConnection.setCursor(
            QtGui.QCursor(QtCore.Qt.ForbiddenCursor))
        self.ILB_StopConnection.setStyleSheet("QLabel{\n"
                                              "    background-color: rgba(50, 60, 50, 200);\n"
                                              "        border-radius:34px;\n"
                                              "border:4px solid rgba(100,100,200,150);\n"
                                              "}\n"
                                              "QLabel::hover{\n"
                                              "    background-color: rgba(200, 100, 200, 100);\n"
                                              "    border:0px solid rgba(100,100,100,150);\n"
                                              "        border-radius:34px;\n"
                                              "}")
        self.ILB_StopConnection.setText("")
        self.ILB_StopConnection.setPixmap(QtGui.QPixmap(
            os.path.join(ICONS_DIR, "system-suspend.png")))
        self.ILB_StopConnection.setScaledContents(True)
        self.ILB_StopConnection.setObjectName("ILB_StopConnection")
        self.horizontalLayout_4.addWidget(self.ILB_StopConnection)
        self.ILB_SearchPorts = QtWidgets.QLabel(self.Connection)
        self.ILB_SearchPorts.setMinimumSize(QtCore.QSize(70, 70))
        self.ILB_SearchPorts.setMaximumSize(QtCore.QSize(80, 80))
        self.ILB_SearchPorts.setCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
        self.ILB_SearchPorts.setStyleSheet("QLabel{\n"
                                           "    background-color: rgba(50, 60, 50, 200);\n"
                                           "        border-radius:40px;\n"
                                           "border:4px solid rgba(100,100,200,150);\n"
                                           "}\n"
                                           "QLabel::hover{\n"
                                           "    background-color: rgba(100, 100, 200, 100);\n"
                                           "    border:0px solid rgba(100,100,100,150);\n"
                                           "        border-radius:40px;\n"
                                           "}")
        self.ILB_SearchPorts.setText("")
        self.ILB_SearchPorts.setPixmap(QtGui.QPixmap(
            os.path.join(ICONS_DIR, "bcompare.png")))
        self.ILB_SearchPorts.setScaledContents(True)
        self.ILB_SearchPorts.setObjectName("ILB_SearchPorts")
        self.horizontalLayout_4.addWidget(self.ILB_SearchPorts)
        self.LB_Port = QtWidgets.QLabel(self.Connection)
        self.LB_Port.setMaximumSize(QtCore.QSize(70, 16777215))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.LB_Port.setFont(font)
        self.LB_Port.setObjectName("LB_Port")
        self.horizontalLayout_4.addWidget(self.LB_Port)
        self.CoBox_Ports = QtWidgets.QComboBox(self.Connection)
        self.CoBox_Ports.setMinimumSize(QtCore.QSize(0, 40))
        self.CoBox_Ports.setMaximumSize(QtCore.QSize(250, 16777215))
        self.CoBox_Ports.setObjectName("CoBox_Ports")

        self.horizontalLayout_4.addWidget(self.CoBox_Ports)
        self.ILB_Connect = QtWidgets.QLabel(self.Connection)
        self.ILB_Connect.setMinimumSize(QtCore.QSize(150, 150))
        self.ILB_Connect.setMaximumSize(QtCore.QSize(150, 150))
        self.ILB_Connect.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.ILB_Connect.setStyleSheet("QLabel{\n"
                                       "    background-color: rgba(50, 60, 50, 200);\n"
                                       "        border-radius:70px;\n"
                                       "border:4px solid rgba(150,200,40,250);\n"
                                       "}\n"
                                       "QLabel::hover{\n"
                                       "    background-color: rgba(100, 100, 200, 100);\n"
                                       "    border:0px solid rgba(100,100,100,150);\n"
                                       "        border-radius:70px;\n"
                                       "}")
        self.ILB_Connect.setText("")
        self.ILB_Connect.setPixmap(QtGui.QPixmap(
            os.path.join(ICONS_DIR, "plexhometheater.png")))
        self.ILB_Connect.setScaledContents(True)
        self.ILB_Connect.setObjectName("ILB_Connect")
        self.horizontalLayout_4.addWidget(self.ILB_Connect)
        self.tabWidget.addTab(self.Connection, "")
        self.About = QtWidgets.QWidget()
        self.About.setObjectName("About")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.About)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.LB_About = QtWidgets.QLabel(self.About)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.LB_About.setFont(font)
        self.LB_About.setObjectName("LB_About")
        self.horizontalLayout_5.addWidget(self.LB_About)
        self.tabWidget.addTab(self.About, "")
        self.verticalLayout_2.addWidget(self.tabWidget)
        self.verticalLayout.addWidget(self.MainFrame)
        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.Thermostat = Thermostat.Thermostat(0)
        self.MessageHandlerThread = MessageHandler()
        self.MessageHandlerThread.signal.connect(self.MessageHandling)

        self.MessageSender = MessageSender()

        self.MaxTemp.valueChanged.connect(self.MaxDialChanged)
        self.MinTemp.valueChanged.connect(self.MinDialChanged)
        self.MinTempVal = 20
        self.MaxTempVal = 30
        self.AvailablePorts = []
        self.SerialConnection = None

        self.ILB_Sound.mouseReleaseEvent = self.SwitchAlarm
        self.PB_Clear.clicked.connect(self.clear)
        self.PB_Save.clicked.connect(self.save)
        self.ILB_Heater.mouseReleaseEvent = self.SwitchHeater
        self.ILB_Cooler.mouseReleaseEvent = self.SwitchCooler
        self.ILB_PowerSave.mouseReleaseEvent = self.SwitchPowerSaving
        self.ILB_SearchPorts.mouseReleaseEvent = self.SearchPorts
        self.ILB_Connect.mouseReleaseEvent = self.ConnectToPort
        self.ILB_StopConnection.mouseReleaseEvent = self.TerminateConnection

        self.SetDisable()
        self.SearchPorts()

        

    def MessageHandling(self,Message:dict,*kwards):
        self.MessageSender.MessageRecived = True
        if list(Message.keys())[0] == "Message":
            _message = Message["Message"]
            _message = _message.split("+")[1]
            if _message == "SettingUp":
                SN = int(Message["Message"].split("+")[0])
                self.Thermostat.SN = SN
                self.MessageHandlerThread.SN = SN
                self.AditionalDialog.show()
                self.ConnectionDialog.LB_Message.setText(f"<html><head/><body><p align=\"center\"><span style=\" font-size:11pt; color:#1899ee;\">USB Connection </span><span style=\" font-size:11pt; color:#37ff00;\">Available</span></p></body></html>")
            elif _message == "FirstStart":
                self.ConnectionDialog.LB_Message.setText(f"<html><head/><body><p align=\"center\"><span style=\" font-size:11pt; color:#1899ee;\">Writhing EEPROM </span><span style=\" font-size:11pt; color:#37ff00;\">OK</span></p></body></html>")
            elif _message == "Ready":
                self.ConnectionDialog.LB_Message.setText(f"<html><head/><body><p align=\"center\"><span style=\" font-size:11pt; color:#1899ee;\">Board is </span><span style=\" font-size:11pt; color:#37ff00;\">Ready</span></p></body></html>")
                AddMessage(b"Get+")
                self.MessageSender.MessageRecived = False
                self.AditionalDialog.close()
                self.MessageHandlerThread.ReadTemp = False
            elif _message == "SensorDetached":
                self.ConnectionDialog.LB_Title.setText("<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; color:#ffb367;\">Sensor</span><span style=\" font-size:14pt;\"> </span><span style=\" font-size:14pt; color:#04ff00;\">Detached :(</span></p></body></html>")
                self.ConnectionDialog.LB_Message.setText(f"<html><head/><body><p align=\"center\"><span style=\" font-size:11pt; color:#1899ee;\">Please check </span><span style=\" font-size:11pt; color:#37ff00;\">DS18B20</span></p></body></html>")
                self.AditionalDialog.show()
                self.ConnectionDialog.BTN_Cancel.clicked.connect(self.TerminateConnection)
                self.SetDisable()
                self.ConnectionDialog.BTN_OK.setEnabled(False)

            elif _message == "SensorAttached":
                self.ConnectionDialog.LB_Title.setText("<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; color:#ffb367;\">Sensor</span><span style=\" font-size:14pt;\"></span><span style=\" font-size:14pt; color:#04ff00;\">Attached :)</span></p></body></html>")
                self.ConnectionDialog.LB_Message.setText(f"<html><head/><body><p align=\"center\"><span style=\" font-size:11pt; color:#1899ee;\">I'm </span><span style=\" font-size:11pt; color:#37ff00;\">Ready</span></p></body></html>")
                self.ConnectionDialog.BTN_Cancel.setEnabled(False)
                self.SetEnable()
                self.ConnectionDialog.BTN_OK.setEnabled(True)
                self.ConnectionDialog.BTN_OK.clicked.connect(self.AditionalDialog.close)
            elif _message == "BatteryLow":
                self.ConnectionDialog.LB_Title.setText("<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; color:#ffb367;\">Battery</span><span style=\" font-size:14pt;\">Low</span><span style=\" font-size:14pt; color:#04ff00;\"></span></p></body></html>")
                self.ConnectionDialog.LB_Message.setText(f"<html><head/><body><p align=\"center\"><span style=\" font-size:11pt; color:#1899ee;\">Please connect </span><span style=\" font-size:11pt; color:#37ff00;\">Charger</span></p></body></html>")
                self.AditionalDialog.show()
                self.ConnectionDialog.BTN_Cancel.clicked.connect(self.TerminateConnection)
                self.SetDisable()
                self.ConnectionDialog.BTN_OK.setEnabled(False)

            elif _message == "BatteryOK":
                self.ConnectionDialog.LB_Title.setText("<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; color:#ffb367;\">Battery </span><span style=\" font-size:14pt;\"></span><span style=\" font-size:14pt; color:#04ff00;\">is ok :)</span></p></body></html>")
                self.ConnectionDialog.LB_Message.setText(f"<html><head/><body><p align=\"center\"><span style=\" font-size:11pt; color:#1899ee;\">I'm </span><span style=\" font-size:11pt; color:#37ff00;\">Ready</span></p></body></html>")
                self.ConnectionDialog.BTN_Cancel.setEnabled(False)
                self.SetEnable()
                self.ConnectionDialog.BTN_OK.setEnabled(True)
                self.ConnectionDialog.BTN_OK.clicked.connect(self.AditionalDialog.close)
            elif _message == "SettingUpdate":
                AddMessage(b"Get+")
                self.MessageSender.MessageRecived = False
                

            if _message in ["HT","LT","HPT","LPT","FDT","FIT","Normal"]:
                self.Thermostat.SetViaStatus(_message)
                self.TempFrame.setStyleSheet(self.TempFrameStyles[self.Thermostat.Status])
                self.UpdateUiViaThermostat()

        elif list(Message.keys())[0] == "Temp":
            self.Thermostat.Temp = Message["Temp"]
            s = str(self.Thermostat.Temp).split(".")[1]
            self.TempLable.setText(f'<html><head/><body><p align="center"><span style=" font-size:26pt; color:#ffffff;">.{s}</span><span style=" font-size:18pt; color:#ffffff;">°C</span></p></body></html>')
            self.TempFrame.setStyleSheet(self.TempFrameStyles[self.Thermostat.Status])
            self.TempMonitor.setProperty("intValue", int(self.Thermostat.Temp))

        elif list(Message.keys())[0] == "Info":
            self.Thermostat.UpdateFromString(Message["Info"])
            self.Thermostat.SetViaAlgoritm()
            self.UpdateUiViaThermostat()
        
        elif list(Message.keys())[0] == "Error":
            if Message["Error"] == "Disconnected":
                self.TerminateConnection()
                self.AditionalDialog.show()
                self.ConnectionDialog.LB_Title.setText("<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; color:#ffb367;\">Connection </span><span style=\" font-size:14pt;\"></span>Fail...<span style=\" font-size:14pt; color:#04ff00;\"></span></p></body></html>")
                self.ConnectionDialog.LB_Message.setText(f"<html><head/><body><p align=\"center\">Please <span style=\" font-size:11pt; color:#1899ee;\"></span><span style=\" font-size:11pt; color:#37ff00;\">Check Connection</span></p></body></html>")
                self.ConnectionDialog.BTN_Cancel.setEnabled(False)
                self.SetDisable()
                self.ConnectionDialog.BTN_OK.setEnabled(True)
                self.ConnectionDialog.BTN_OK.clicked.connect(self.AditionalDialog.close)

    def UpdateBatteryUi(self,*kwards):
        Voltage = self.Thermostat.BatteryVoltage
        """
        pers = (VCC*(90+VCC*10-30)*2)-740
        100% = 4.2V
        90% = 4.1
        80% = 4.0
        60% = 3.9
        40% = 3.8
        pers = (VCC*(91+VCC*10-30)*2)-740
        0% = 3.7
        """
        icon = ""
        pers = 0
        if Voltage < 3.8:
            pers = int((Voltage*(91+Voltage*10-30)*2)-740)
        else:
            pers = int((Voltage*(90+Voltage*10-30)*2)-740)
        
        if pers <= 5:
            icon = self.BatteryImages["0"]
        elif pers <= 10:
            icon = self.BatteryImages["1"]
        elif pers <= 20:
            icon = self.BatteryImages["2"]
        elif pers <= 40:
            icon = self.BatteryImages["3"]
        elif pers <= 60:
            icon = self.BatteryImages["2"]
        elif pers <= 80:
            icon = self.BatteryImages["3"]
        elif pers <= 90:
            icon = self.BatteryImages["4"]
        elif pers <= 100:
            icon = self.BatteryImages["5"]
        elif pers >100:
            icon = self.BatteryImages["F"]
            pers = 100
        self.LB_BT.setPixmap(QtGui.QPixmap(os.path.join(ICONS_DIR, icon)))
        self.LB_BatteryPers.setText(f"<html><head/><body><p align=\"center\">{int(pers)}%</p></body></html>")
        self.LB_ChargeTime.setText(f"<html><head/><body><p align=\"center\">About </p><p align=\"center\">{int(self.Thermostat.BatteryCapacity/200*(pers/100))} Hour</p></body></html>")
    
    def UpdateUiViaThermostat(self,*kwards):
        self.TempMonitor.setProperty("intValue", int(self.Thermostat.Temp))
        s = str(self.Thermostat.Temp).split(".")[1]
        self.TempLable.setText(f'<html><head/><body><p align="center"><span style=" font-size:26pt; color:#ffffff;">.{s}</span><span style=" font-size:18pt; color:#ffffff;">°C</span></p></body></html>')

        if self.Thermostat.PowerSaving:
            self.ILB_PowerSave.setStyleSheet("QLabel{\n"
                                        "    background-color: rgba(50, 200, 50, 200);\n"
                                        "        border-radius:35px;\n"
                                        "border:4px solid rgba(100,100,100,250);\n"
                                        "}\n"
                                        "QLabel::hover{\n"
                                        "    background-color: rgba(100, 100, 200, 100);\n"
                                        "    border:0px solid rgba(100,100,100,150);\n"
                                        "        border-radius:35px;\n"
                                        "}")
        else:
            self.ILB_PowerSave.setStyleSheet("QLabel{\n"
                                    "    background-color: rgba(250, 0, 0, 200);\n"
                                      
                                      "        border-radius:35px;\n"
                                      "border:4px solid rgba(100,100,100,250);\n"
                                      "}\n"
                                      "QLabel::hover{\n"
                                      "    background-color: rgba(40, 150, 50, 200);\n"
                                      "    border:0px solid rgba(100,100,100,150);\n"
                                      "        border-radius:35px;\n"
            "}")
        if self.Thermostat.AlarmState == 0:
            self.ILB_Sound.setPixmap(QtGui.QPixmap(os.path.join(ICONS_DIR, "sound_mute.png")))
            self.ILB_Cooler.setStyleSheet("QLabel{\n"
                                    "    background-color: rgba(250, 0, 0, 200);\n"
                                      
                                      "        border-radius:70px;\n"
                                      "border:4px solid rgba(100,100,100,250);\n"
                                      "}\n"
                                      "QLabel::hover{\n"
                                      "    background-color: rgba(40, 150, 50, 200);\n"
                                      "    border:0px solid rgba(100,100,100,150);\n"
                                      "        border-radius:70px;\n"
            "}")
        elif self.Thermostat.AlarmState == 1:
            self.ILB_Sound.setPixmap(QtGui.QPixmap(os.path.join(ICONS_DIR, "sound.png")))
            self.ILB_Cooler.setStyleSheet("QLabel{\n"
                                    "    background-color: rgba(50, 200, 50, 200);\n"
                                      
                                      "        border-radius:70px;\n"
                                      "border:4px solid rgba(100,100,100,250);\n"
                                      "}\n"
                                      "QLabel::hover{\n"
                                      "    background-color: rgba(40, 150, 50, 200);\n"
                                      "    border:0px solid rgba(100,100,100,150);\n"
                                      "        border-radius:70px;\n"
            "}")
        elif self.Thermostat.AlarmState == 2:
            self.ILB_Sound.setPixmap(QtGui.QPixmap(os.path.join(ICONS_DIR, "sound_ok.png")))
            self.ILB_Cooler.setStyleSheet("QLabel{\n"
                                    "    background-color: rgba(50, 200, 50, 200);\n"
                                      
                                      "        border-radius:70px;\n"
                                      "border:4px solid rgba(100,100,100,250);\n"
                                      "}\n"
                                      "QLabel::hover{\n"
                                      "    background-color: rgba(40, 150, 50, 200);\n"
                                      "    border:0px solid rgba(100,100,100,150);\n"
                                      "        border-radius:70px;\n"
            "}")  

        if self.Thermostat.Cooler:
            self.ILB_Cooler.setStyleSheet("QLabel{\n"
                                        "    background-color: rgba(50, 60, 50, 200);\n"
                                        "        border-radius:70px;\n"
                                        "border:4px solid rgba(100,100,100,250);\n"
                                        "}\n"
                                        "QLabel::hover{\n"
                                        "    background-color: rgba(100, 100, 200, 100);\n"
                                        "    border:0px solid rgba(100,100,100,150);\n"
                                        "        border-radius:70px;\n"
                                        "}")
            if self.Thermostat.CoolerState == 2:
                self.ILB_Cooler.setMovie(self.CoolerOn)
                self.CoolerOn.start()
            else:
                self.ILB_Cooler.setPixmap(self.CoolerOff)
                self.CoolerOn.stop()

        else:
            self.CoolerOn.stop()
            self.ILB_Cooler.setPixmap(self.CoolerOff)
            self.ILB_Cooler.setStyleSheet("QLabel{\n"
                                    "    background-color: rgba(250, 0, 0, 200);\n"
                                      
                                      "        border-radius:70px;\n"
                                      "border:4px solid rgba(100,100,100,250);\n"
                                      "}\n"
                                      "QLabel::hover{\n"
                                      "    background-color: rgba(40, 150, 50, 200);\n"
                                      "    border:0px solid rgba(100,100,100,150);\n"
                                      "        border-radius:70px;\n"
            "}")
        if self.Thermostat.Heater:
            self.ILB_Heater.setStyleSheet("QLabel{\n"
                                        "    background-color: rgba(50, 60, 50, 200);\n"
                                        "        border-radius:70px;\n"
                                        "border:4px solid rgba(100,100,100,250);\n"
                                        "}\n"
                                        "QLabel::hover{\n"
                                        "    background-color: rgba(100, 100, 200, 100);\n"
                                        "    border:0px solid rgba(100,100,100,150);\n"
                                        "        border-radius:70px;\n"
                                        "}")
            if self.Thermostat.HeaterState == 2:
                self.ILB_Heater.setMovie(self.HeaterOn)
                self.HeaterOn.start()
            else:
                self.ILB_Heater.setPixmap(self.HeaterOff)
                self.HeaterOn.stop()

        else:
            self.HeaterOn.stop()
            self.ILB_Heater.setPixmap(self.HeaterOff)
            self.ILB_Heater.setStyleSheet("QLabel{\n"
                                    "    background-color: rgba(250, 0, 0, 200);\n"
                                      
                                      "        border-radius:70px;\n"
                                      "border:4px solid rgba(100,100,100,250);\n"
                                      "}\n"
                                      "QLabel::hover{\n"
                                      "    background-color: rgba(40, 150, 50, 200);\n"
                                      "    border:0px solid rgba(100,100,100,150);\n"
                                      "        border-radius:70px;\n"
            "}")
        
        self.UpdateDials()
        self.UpdateBatteryUi()

    def UpdateDials(self,*kwards):
        MaxVal = int(self.Thermostat.MaxTemp)
        MinVal = int(self.Thermostat.MinTemp)
        self.LB_MaxTemp.setText(f"<html><head/><body><p align=\"center\">{MaxVal}</p></body></html>")
        if MaxVal > 0:
            MaxVal = 0-MaxVal
        elif MaxVal < 0:
            MaxVal = abs(MaxVal)
        
        self.MaxTempVal = MaxVal
        self.MinTempVal = MinVal
        self.LB_MinTemp.setText(f"<html><head/><body><p align=\"center\">{MinVal}</p></body></html>")
        self.MinTemp.setValue(MinVal)
        self.MaxTemp.setValue(MaxVal)
        self.BTN_Frame.setVisible(False)

    def TerminateConnection(self,*kwards):
        try:
            self.MessageSender.quit()
            self.MessageHandlerThread.quit()
            print(self.SerialConnection.Disconnect())
            self.CoBox_Ports.clear()
            self.SetDisable()
        except Exception as e:print(e)
        

    def ConnectToPort(self,*kwards):
        PortName = self.CoBox_Ports.currentText()
        PortInfo = self.AvailablePorts[PortName]
        self.AditionalDialog.show()
        self.ConnectionDialog.LB_Title.setText(f"<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; color:#ffb367;\">Connecting </span><span style=\" font-size:14pt;\">To... </span><span style=\" font-size:14pt; color:#04ff00;\">{PortName}</span></p></body></html>")
        self.ConnectionDialog.LB_Message.setText("")
        self.ConnectionDialog.BTN_Cancel.clicked.connect(self.TerminateConnection)
        self.ConnectionDialog.BTN_OK.setEnabled(False)
        Tryes = 4
        self.SerialConnection = Connection.SerialPort(PortName,PortInfo.get("baudrate"),Name = PortName)
        res = ""
        while True:
            try:
                res = self.SerialConnection.Connect()
                if res == "Connected":
                    self.MessageSender.connection = self.SerialConnection
                    self.MessageHandlerThread.connection = self.SerialConnection
                    self.MessageHandlerThread.start()
                    self.MessageSender.start()
                    self.SetEnable()
                    self.clear()
                    break
                else:
                    Tryes -= 1
                    if Tryes == 0:
                        break
            except:pass


    def SearchPorts(self,*kwards):
        Ports = Connection.SearchSerialports()
        self.CoBox_Ports.clear()
        self.AvailablePorts = Ports
        for name,info in Ports.items():
            self.CoBox_Ports.addItem(name)
        if len(Ports)>0:
            self.ILB_Connect.setEnabled(True)
        else:self.ILB_Connect.setEnabled(False)

    def SetDisable(self,*kwards):
        self.BTN_Frame.setVisible(False)
        self.tabWidget.setCurrentIndex(1)
        self.ILB_StopConnection.setEnabled(False)
        self.ILB_Connect.setEnabled(False)
        self.TempFrame.setEnabled(False)
        self.setting.setEnabled(False)
        self.ILB_Cooler.setPixmap(self.CoolerOff)
        self.ILB_Heater.setPixmap(self.HeaterOff)
        if self.CoBox_Ports.currentText():
            self.ILB_Connect.setEnabled(True)
        self.ILB_SearchPorts.setEnabled(True)

    def SetEnable(self,*kwards):
        self.ILB_Connect.setEnabled(False)
        self.ILB_SearchPorts.setEnabled(False)
        self.BTN_Frame.setVisible(True)
        self.tabWidget.setCurrentIndex(0)
        self.ILB_StopConnection.setEnabled(True)
        self.TempFrame.setEnabled(True)
        self.setting.setEnabled(True)
        self.BTN_Frame.setVisible(False)

    def SwitchPowerSaving(self,*kwards):
        if self.Thermostat.PowerSaving == 1:
            AddMessage(self.SerialConnection.GetCommandMessage(PowerSavingMode=0)) 
        else:
            AddMessage(self.SerialConnection.GetCommandMessage(PowerSavingMode=1)) 
        self.MessageSender.MessageRecived = False

    def SwitchCooler(self,*kwards):
        if self.Thermostat.Cooler == 1:
            AddMessage(self.SerialConnection.GetCommandMessage(CoolerState=0)) 
        else:
            AddMessage(self.SerialConnection.GetCommandMessage(CoolerState=1)) 
        self.MessageSender.MessageRecived = False

    def SwitchHeater(self,*kwards):
        if self.Thermostat.Heater == 1:
            AddMessage(self.SerialConnection.GetCommandMessage(HeaterState=0)) 
        else:
            AddMessage(self.SerialConnection.GetCommandMessage(HeaterState=1)) 
        self.MessageSender.MessageRecived = False

    def SwitchAlarm(self,*kwards):
        if self.Thermostat.Alarm == 1:
            AddMessage(self.SerialConnection.GetCommandMessage(AlarmState=0)) 
        else:
            AddMessage(self.SerialConnection.GetCommandMessage(AlarmState=1)) 
        self.MessageSender.MessageRecived = False

    def save(self):
        self.BTN_Frame.setVisible(False)
        AddMessage(self.SerialConnection.GetCommandMessage(MaxTemp=self.MaxTempVal,MinTemp=self.MinTempVal)) 
        self.MessageSender.MessageRecived = False

    def clear(self):
        self.MaxTempVal = int(self.Thermostat.MaxTemp)
        self.MinTempVal = int(self.Thermostat.MinTemp)
        self.MinTemp.setValue(self.MinTempVal)

        if self.MaxTempVal > 0:
            self.MaxTemp.setValue(0-self.MaxTempVal)
        elif self.MaxTempVal < 0:
            self.MaxTemp.setValue(abs(self.MaxTempVal))
        else:
            self.MinTemp.setValue(self.MaxTempVal)
        self.MaxDialChanged()
        self.MinDialChanged()
        self.BTN_Frame.setVisible(False)

    def MaxDialChanged(self,ShowFrame = True):
        MaxVal = self.MaxTemp.value()
        MinVal = self.MinTemp.value()
        if MaxVal > 0:
            MaxVal = 0-MaxVal
        elif MaxVal < 0:
            MaxVal = abs(MaxVal)
        self.MaxTempVal = MaxVal
        self.LB_MaxTemp.setText(f"<html><head/><body><p align=\"center\">{MaxVal}</p></body></html>")
        if(MaxVal <= MinVal):
            self.MinTemp.setValue(MaxVal-1)
            self.MinDialChanged()
        if MaxVal != int(self.Thermostat.MaxTemp) and ShowFrame:
            self.BTN_Frame.setVisible(True)

    def MinDialChanged(self,ShowFrame = True):
        MinVal = self.MinTemp.value()
        self.MinTempVal = MinVal
        self.LB_MinTemp.setText(f"<html><head/><body><p align=\"center\">{MinVal}</p></body></html>")
        if(MinVal >= self.MaxTempVal):
            self.MaxTempVal = MinVal +1
            nv = 0
            if MinVal >0:
                nv = 0 - MinVal
            elif MinVal <0:
                nv = abs(MinVal)
            self.MaxTemp.setValue(nv-1)
            self.MaxDialChanged()
        if MinVal != int(self.Thermostat.MinTemp) and ShowFrame:
            self.BTN_Frame.setVisible(True)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Saniar_Mf"))
        self.GB_MinTemp.setTitle(_translate(
            "MainWindow", "Minimum Temprature"))
        self.LB_MinTemp.setText(_translate(
            "MainWindow", f"<html><head/><body><p align=\"center\"><span style=\" color:#ffffff;\">-49</span></p></body></html>"))
        self.TempLable.setText(_translate(
            "MainWindow", "<html><head/><body><p align=\"center\"><span style=\" color:#ffffff;\">°C</span></p></body></html>"))
        self.GB_MaxTemp.setTitle(_translate(
            "MainWindow", "Maximum Temprature"))
        self.LB_MaxTemp.setText(_translate(
            "MainWindow", f"<html><head/><body><p align=\"center\">124</p></body></html>"))
        self.PB_Clear.setText(_translate("MainWindow", "Clear"))
        self.PB_Save.setText(_translate("MainWindow", "Save"))
        self.LB_BatteryPers.setText(_translate(
            "MainWindow", "<html><head/><body><p align=\"center\">87%</p></body></html>"))
        self.LB_ChargeTime.setText(_translate(
            "MainWindow", "<html><head/><body><p align=\"center\">About </p><p align=\"center\">18 Hour</p></body></html>"))
        self.ILB_Cooler.setToolTip(_translate(
            "MainWindow", "<html><head/><body><p>Cooler System Controller</p></body></html>"))
        self.ILB_Sound.setToolTip(_translate(
            "MainWindow", "<html><head/><body><p>Sound alarm</p></body></html>"))
        self.ILB_Heater.setToolTip(_translate(
            "MainWindow", "<html><head/><body><p>Heater System Controller</p></body></html>"))
        self.ILB_PowerSave.setToolTip(_translate(
            "MainWindow", "<html><head/><body><p>Power Saving Mode</p></body></html>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(
            self.setting), _translate("MainWindow", "Setting"))
        self.ILB_StopConnection.setToolTip(_translate(
            "MainWindow", "<html><head/><body><p>Disconnect</p></body></html>"))
        self.ILB_SearchPorts.setToolTip(_translate(
            "MainWindow", "<html><head/><body><p>Search Ports</p></body></html>"))
        self.LB_Port.setText(_translate("MainWindow", "Port:"))
        self.ILB_Connect.setToolTip(_translate(
            "MainWindow", "<html><head/><body><p>Connect</p></body></html>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(
            self.Connection), _translate("MainWindow", "Connection"))
        self.LB_About.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\">Made with <span style=\" color:#ff585b;\">Love</span> by <span style=\" color:#a0ff60;\">Mohammad Mofidi </span></p><p align=\"center\">#2 <span style=\" color:#00b3ff;\">Technical</span> university of <span style=\" color:#00d8b4;\">Tabriz</span>/Iran<span style=\" font-size:8pt; color:#78abf7;\">/Asia/Earth/S</span><span style=\" font-family:\'Hack\'; font-size:8pt; color:#78abf7;\">olarSystem/MilkyWay &amp;...:)</span></p><p align=\"center\"><a href=\"https://github.com/saniar-mf/\"><span style=\" text-decoration: underline; color:#e28c01;\">https://github.com/saniar-mf/</span></a></p><p align=\"center\">©GNU License</p></body></html>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(
            self.About), _translate("MainWindow", "About"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Breeze')
    # app.setStyle('Windows')
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
