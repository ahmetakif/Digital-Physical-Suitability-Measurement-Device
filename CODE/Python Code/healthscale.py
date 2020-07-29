
from appJar import *
import serial.tools.list_ports
import pandas as pd
import serial
import time

def findArduinoPort(serialBaudrate='9600', cooldown=1):

    arduinoPort = None
    ports = list(serial.tools.list_ports.comports())

    if len(ports) > 1:
    
        for port in ports:

            if 'Arduino' in port.description or 'CH340' in port.description:

                arduinoPort = str(port.device)
                break

    else:

        arduinoPort = str(ports[0].device)

    return serial.Serial(arduinoPort, baudrate=serialBaudrate, timeout=cooldown)

def defSerialConn(arduinoPort, serialBaudrate=9600, cooldown=1):

    return serial.Serial(arduinoPort, baudrate=serialBaudrate, timeout=cooldown)

def mainThread():

    global filePath, studentIndex, df
    studentIndex = 0
    
    while True:

        if 'filePath' in globals():
            if studentIndex == len(df):

                app.disableButton('Kaydet')
                app.disableButton('Öğrenci Yok')

                app.queueFunction(app.setLabel, 'nextStudent', 'Bütün öğrencilerin ölçümü yapıldı. Lütfen başka bir sınıfı seçiniz.')
        
        output = ser.readline().decode()
        output = output.split(',')
        
        if 'height' and 'scale' in output:
            
            height = output[1]
            weight = output[3]

            app.queueFunction(app.setLabel, 'heightVar', height + ' cm')
            app.queueFunction(app.setLabel, 'weightVar', weight + ' kg')

            app.queueFunction(app.setLabel, 'waitLabel', 'Boy ve kilo ölçümü tamamlanmıştır.')
            app.queueFunction(app.setLabel, 'infStatus', '')
            time.sleep(2)

            app.hideSubWindow('Bekleniyor')
            app.show()

            app.queueFunction(app.setLabel, 'waitLabel', 'Lütfen Bekleyiniz')
            app.queueFunction(app.setLabel, 'infStatus', '-')

        elif 'r' in output:

            app.infoBox('Onay', 'Devam etmek için "OK" butonuna basınız')

            time.sleep(0.5)
            
            ser.write(b'c')

        elif 'strech' in output:

            strech = output[1]
            strechPoint = output[2]

            app.queueFunction(app.setLabel, 'strechVar', strech + ' cm')
            app.queueFunction(app.setLabel, 'pointVar', strechPoint + '/10')

            app.queueFunction(app.setLabel, 'waitLabel', 'Esneklik ölçümü tamamlanmıştır.')
            app.queueFunction(app.setLabel, 'infStatus', '')
            time.sleep(2)

            app.hideSubWindow('Bekleniyor')
            app.show()

            app.queueFunction(app.setLabel, 'waitLabel', 'Lütfen Bekleyiniz')
            app.queueFunction(app.setLabel, 'infStatus', '-')

        elif 'writemode' in output:

            height = output[1]
            weight = output[2]
            strech = output[3]
            strechPoint = output[4]

            
            if height == '0.00' or weight == '0.00' or strech == '0.00' or strechPoint == '0.00':

                app.infoBox('Hata', 'Bütün ölçümleri yaptığınızdan emin olunuz.')
            
            else:

                #bmi = int(weight)/((int(height)/100)**2)
                #bmiStatus = getbmiStatus(bmi)

                bmi = 1
                bmiStatus = 1
                
                app.queueFunction(app.setLabel, 'heightVar', height + ' cm')
                app.queueFunction(app.setLabel, 'weightVar', weight + ' kg')
                app.queueFunction(app.setLabel, 'strechVar', strech + ' cm')
                app.queueFunction(app.setLabel, 'pointVar', strechPoint + '/10')

                a = df.iloc[studentIndex][0]
                b = df.iloc[studentIndex][1]
                c = df.iloc[studentIndex][2]
                studentName = df.iloc[studentIndex][3]
                studentSur = df.iloc[studentIndex][4]
                
                df.loc[studentIndex] = [a, b, c, studentName, studentSur, height, weight, strech, bmi, bmiStatus]

                studentIndex += 1

                df.to_excel(filePath, index=False)
            
                app.infoBox('Bilgi', 'Öğrencinin ölçümü başarıyla tamamlanıp kaydedildi.')

                app.queueFunction(app.setLabel, 'nextStudent', 'Sıradaki Öğrenci: ' + df.iloc[studentIndex][3] + ' ' + df.iloc[studentIndex][4])
                
                app.queueFunction(app.setLabel, 'heightVar', '- cm')
                app.queueFunction(app.setLabel, 'weightVar', '- kg')
                app.queueFunction(app.setLabel, 'strechVar', '- cm')
                app.queueFunction(app.setLabel, 'pointVar', '-/10')

                height = 0
                weight = 0
                strech = 0
                strechPoint = 0
                bmi = None
                bmiStatus = None

                a = None
                b = None
                c = None
                studentName = None
                studentSur = None
            
        elif 'calibration' in output:

            app.hideSubWindow('Kalibrasyon')
            app.infoBox('Bilgi', 'Kalibrasyon işlemi başarıyla tamamlanmıştır.')
            app.showSubWindow('Kullanim Talimatlari')

def sendSerialMsg(button):

    if button == 'Boy ve Kilo Ölç':

        ser.write(b'o')

        app.setLabel('infStatus', 'Boy ve kilo ölçülüyor...')

        app.hide()
        app.showSubWindow('Bekleniyor')

    elif button == 'Esneklik Ölç':

        ser.write(b'k')

        app.setLabel('infStatus', 'Esneklik ölçülüyor...')

        app.hide()
        app.showSubWindow('Bekleniyor')

    elif button == 'Kaydet':

        ser.write(b'w')

    elif button == 'Kalibre Et':

        ser.write(b's')

def getbmiStatus(bmi):

    if bmi <= 18.5:

        return 'Düşük Kilolu'

    elif bmi <= 24.9:

        return 'Normal Kilolu'
        
    elif bmi <= 29.9:

        return 'Fazla Kilolu'

    elif bmi <= 39.9:

        return 'Obez'

    else:
        
        return 'Aşırı Obez'

def startMainGUI():

    app.hideSubWindow('Kullanim Talimatlari')
    app.show()

def startingThread():
    
    app.thread(mainThread)

def selectClass():

    global filePath, df, studentIndex

    filePath = app.openBox(title='Sınıf Listesi Seçiniz', fileTypes=[('Microsoft Excel dosyası', '*.xlsx')], asFile=False, parent=None, multiple=False, mode='r')
    df = pd.read_excel(filePath, indexCol=0)

    properFile = filePath.split('/')[-1]
    properFileName = properFile.split('.')[0]
    
    app.infoBox('Bilgi', f"""{properFileName} sınıfının listesi başarıyla seçilmiştir.
Bu listede {len(df)} kişi vardır.""")

    studentIndex = 0
    
    app.setLabel('heightVar', '- cm')
    app.setLabel('weightVar', '- kg')
    app.setLabel('strechVar', '- cm')
    app.setLabel('pointVar', '-/10')

    app.enableButton('Kaydet')
    app.enableButton('Öğrenci Yok')
        
    app.setLabel('nextStudent', 'Şimdiki Öğrenci: ' + df.iloc[0][3] + ' ' + df.iloc[0][4])
    app.topLevel.update()

def noStudent():

    global studentIndex

    a = df.iloc[studentIndex][0]
    b = df.iloc[studentIndex][1]
    c = df.iloc[studentIndex][2]
    studentName = df.iloc[studentIndex][3]
    studentSur = df.iloc[studentIndex][4]
    
    df.iloc[studentIndex] = [a, b, c, studentName, studentSur, '', '', '', '', '']

    df.to_excel(filePath)

    studentIndex += 1

    app.setLabel('nextStudent', 'Şimdiki Öğrenci: ' + df.iloc[studentIndex][3] + ' ' + df.iloc[studentIndex][4])
    
    app.setLabel('heightVar', '- cm')
    app.setLabel('weightVar', '- kg')
    app.setLabel('strechVar', '- cm')
    app.setLabel('pointVar', '-/10')


    print(df.head)
    
#Defining a dataframe for excel

#Manually define serial port
#arduinoPort = 'COM3'
#ser = defSerialConn(arduinoPort)

#Automatically find serial port
ser = findArduinoPort()

time.sleep(4)#Waiting Arduino

#GUI initialization
app = gui('Boy Kutle')

app.setBg('black')
app.setFg('yellow')
app.setFont(family='Open Sans', size=30)

#Calibration GUI
app.startSubWindow('Kalibrasyon')

app.setBg('black')
app.setFg('yellow')

app.addLabel('Hoşgeldiniz')
app.addLabel('Kalibrasyon yapmak için aşağıdaki butona basınız')
app.addButton('Kalibre Et', sendSerialMsg)

app.stopSubWindow()

#Help GUI
app.startSubWindow('Kullanim Talimatlari')

app.setBg('black')
app.setFg('yellow')

app.addLabel('Kullanım Talimatlar')
app.addLabel('Adım 1: {text}')
app.addLabel('Adım 2: {text}')
app.addLabel('Adım 3: {text}')
app.addLabel('Adım 4: {text}')
app.addLabel('Adım 5: {text}')
app.addButton('Devam Et', startMainGUI)

app.stopSubWindow()

#Information GUI
app.startSubWindow('Bekleniyor')

app.setBg('black')
app.setFg('yellow')

app.addLabel('waitLabel', 'Lütfen Bekleyiniz')
app.addLabel('infStatus', '-')

app.stopSubWindow()

#
#   MAIN GUI
#

#Copytight text
app.addLabel('copyright', 'Dijital Fiziksel Uygunluk Cihazı')

app.getLabelWidget('copyright').config(font=('Open Sans', '40', 'normal'))

#General frame(to protect page layout)
app.startFrame('widgets')

#First frame(about height and weight values)
app.startFrame('heightandweight', row=1, column=0)

app.startFrame('h&w-labels')#frame for labels
app.addLabel('Boy', row=0, column=0)
app.addLabel('heightVar', '- cm', row=1, column=0)
app.addLabel('Kilo', row=0, column=1)
app.addLabel('weightVar', '- kg', row=1, column=1)
app.stopFrame()#"withoutbutton" frame

app.addButton('Boy ve Kilo Ölç', sendSerialMsg)
app.stopFrame()#"h&w-labels" frame

app.addVerticalSeparator(1, 1, rowspan=1, colour='green')

#Second frame(about strech values)
app.startFrame('strech', row=1, column=2)

app.startFrame('strech-labels')
app.addLabel('Esneklik', row=0, column=0)
app.addLabel('strechVar', '- cm', row=1, column=0)
app.addLabel('Esneklik Derecesi', row=0, column=1)
app.addLabel('pointVar', '-/10', row=1, column=1)
app.stopFrame()#"strech-labels" frame

app.addButton('Esneklik Ölç', sendSerialMsg)
app.stopFrame()#"strech" frame

app.stopFrame() #"widget" frame

app.addLabel('nextStudent', 'Şimdiki Öğrenci: -')

app.startFrame('bottomButtons')
app.addButton('Sınıf Listesi Seç', selectClass, row=0, column=0)
app.addButton('Öğrenci Yok', noStudent, row=0, column=1)
app.addButton('Kaydet', sendSerialMsg, row=0, column=2)
app.stopFrame()

#Adjusting button appearance
buttons = ['Kalibre Et', 'Devam Et', 'Boy ve Kilo Ölç', 'Esneklik Ölç', 'Sınıf Listesi Seç', 'Öğrenci Yok', 'Kaydet']

for button in buttons:

    app.setButtonRelief(button, 'groove')
    app.setButtonBg(button, 'black')
    app.setButtonFg(button, 'yellow')

app.disableButton('Kaydet')
app.disableButton('Öğrenci Yok')

#Running startingThread() function on start
app.setStartFunction(startingThread)

app.go(startWindow='Kalibrasyon')
