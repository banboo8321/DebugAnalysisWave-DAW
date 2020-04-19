from PyQt5.QtWidgets import QPushButton,QWidget,QApplication,QGridLayout,QListWidget,QLineEdit
import pyqtgraph as pg
import sys
import array
import serial
import threading
import numpy as np
import time
from queue import Queue

sampling_time = 100
i = 0
historyLength = 100  # 横坐标长度 time: n second = 10 ms * n00
currentLength = historyLength
Start_record = False
data_update = False
first_data_update = False
def config_uart():
    # User input comport and bundrate
    comport = 'COM3'
    baudrate = 115200
    #comport = input('Please input comport (like COM3) for your connected device: ')
    #baudrate = input('Please input baudrate (like 9600) for your connected device: ')
    bytes = input('Please input bytes type of uart data (1->1 byte, 2->2 bytes): ')
    bytes = int(bytes)
    print('You selected %s, baudrate %d, %d byte.' % (comport, int(baudrate), bytes))
        # 串口执行到这已经打开 再用open命令会报错
    mSerial = serial.Serial(comport, int(baudrate))
    if (mSerial.isOpen()):
        print("open success")
        mSerial.write("hello DAW\r\n".encode()) # 向端口些数据 字符串必须译码
        mSerial.flushInput()  # 清空缓冲区
    else:
        print("open failed")
        serial.close()  # 关闭端口
        
def checksum(data_r):
	#n_position = data_r.list('\n')
	#in_checksum = data_r[n_position-1]
	sum = 0
	for ii in data_r:
		sum = sum+ii
	sum = sum - 9  #  -10+1	due to add 0x0a
	#print(sum)
	if(sum%256 == 0):
		return True
	else:
		return False
        
def Serial():
    while(True):
        while mSerial.isOpen():
            try:
                #print("waiting for connect data ...")
                if mSerial.inWaiting():
                    data_r = int.from_bytes(mSerial.readline(1),byteorder='little')  
                    global Start_record,data_update,first_data_update
                    if Start_record:
                        data.append(data_r)
                        if data_r == 10 :#0x0A
                            #print('start convert data1')
                            data1.append(data[-6])
                            data2.append(data[-5])
                            data3.append(data[-4])
                            data4.append(data[-3])
                            data5.append(data[-2])
                            data6.append(data[-1])
                            #print('data3',data3)
                            data_update = True
                            first_data_update = True
                    #if(checksum(data_r) == True): #receive a package data
                    #    if Start_record:
                        #add D1 to q1 ...

            except:
                print("serial port except & disconnect\r\n")
                break
                            
                            
                           
class DebugAnalysisWave(QWidget):
    def __init__(self):
        super(DebugAnalysisWave, self).__init__()
        self.initUI()
        self.linePlot1()
        self.linePlot2()
        self.linePlot3()
        self.linePlot4()
        self.linePlot5()
        self.linePlot6()
        #self.plotData()
        #self.scatterPlot()
        #self.three_curves()

    def initUI(self):
        self.setGeometry(400,400,800,620)
        self.setWindowTitle("DAW - Debug Analysis Wave")

        ## 创建一些小部件放在顶级窗口中
        #btn = QPushButton('Start')
        self.btn_1=QPushButton("Start")
        self.btn_2=QPushButton("Stop")
        self.btn_3=QPushButton("exit")
        text = QLineEdit('enter comport')
        listw = QListWidget()
        listw.addItems(["aa", "bb", "cc"])



        self.btn_1.setCheckable(True)#设置已经被点击
        self.btn_1.toggle()#切换按钮状态
        self.btn_1.clicked.connect(self.btnState)
        #self.btn_1.clicked.connect(lambda :self.wichBtn(self.btn_1))

        #self.btn_2.setIcon(QIcon('./image/add_16px_1084515_easyicon.net.ico'))#按钮按钮
        #self.btn_2.setIcon(QIcon(QPixmap('./image/baidu.png')))
        self.btn_2.setEnabled(False)#设置不可用状态
        self.btn_2.toggle()#切换按钮状态
        self.btn_2.clicked.connect(self.btn2State)
        #self.btn_2.clicked.connect(lambda :self.wichBtn(self.btn_2))
        
        self.btn_3.setCheckable(True)#设置已经被点击
        self.btn_3.toggle()#切换按钮状态
        self.btn_3.clicked.connect(self.btn3State)
        
        self.gridLayout = QGridLayout(self)
        ## 将部件添加到布局中的适当位置
        self.gridLayout.addWidget(self.btn_1, 0, 0)
        self.gridLayout.addWidget(self.btn_2, 1, 0)
        self.gridLayout.addWidget(text, 2, 0)
        self.gridLayout.addWidget(self.btn_3, 3, 0)

        self.setLayout(self.gridLayout)
    def btnState(self):
        global Start_record;
        print("Btn_1 was clicked")
        Start_record = True
        self.btn_1.setEnabled(False)#设置不可用状态
        self.btn_2.setEnabled(True)#设置可用状态

    def btn2State(self):
        global Start_record,first_data_update
        print("Btn_2 was clicked")
        Start_record = False
        first_data_update = False
        self.btn_2.setEnabled(False)#设置不可用状态
        self.btn_1.setEnabled(True)#设置可用状态  
    def btn3State(self):
        print("Btn_3 was clicked")
        sys.exit(app.exec_())
    def linePlot1(self):
        p1.showGrid(x=True, y=True)  # 把X和Y的表格打开
        p1.setRange(xRange=[0, historyLength], yRange=[0, 255], padding=0)
        p1.setLabel(axis='left', text='y / V')  # 靠左
        p1.setLabel(axis='bottom', text='x 0.1s')
        p1.setTitle('DAW - p1')  # 表格的名字
        curve1 = p1.plot(pen = 'y')  # 绘制一个图形
        curve1.setData(data)
        self.gridLayout.addWidget(p1, 0, 1, 1, 1)
    def linePlot2(self):
        p2.showGrid(x=True, y=True)  # 把X和Y的表格打开
        p2.setRange(xRange=[0, historyLength], yRange=[0, 255], padding=0)
        p2.setLabel(axis='left', text='y / V')  # 靠左
        p2.setLabel(axis='bottom', text='x 0.1s')
        p2.setTitle('DAW - p2')  # 表格的名字
        curve2 = p2.plot()  # 绘制一个图形
        curve2.setData(data)
        self.gridLayout.addWidget(p2, 1, 1, 1, 1)
    def linePlot3(self):
        p3.showGrid(x=True, y=True)  # 把X和Y的表格打开
        p3.setRange(xRange=[0, historyLength], yRange=[0, 255], padding=0)
        p3.setLabel(axis='left', text='y / V')  # 靠左
        p3.setLabel(axis='bottom', text='x 0.1s')
        p3.setTitle('DAW - p3')  # 表格的名字
        curve2 = p3.plot()  # 绘制一个图形
        curve2.setData(data)
        self.gridLayout.addWidget(p3, 2, 1, 1, 1)
    def linePlot4(self):
        p4.showGrid(x=True, y=True)  # 把X和Y的表格打开
        p4.setRange(xRange=[0, historyLength], yRange=[0, 255], padding=0)
        p4.setLabel(axis='left', text='y / V')  # 靠左
        p4.setLabel(axis='bottom', text='x 0.1s')
        p4.setTitle('DAW - p4')  # 表格的名字
        curve2 = p4.plot()  # 绘制一个图形
        curve2.setData(data)
        self.gridLayout.addWidget(p4, 0, 2, 1, 1)
    def linePlot5(self):
        p5.showGrid(x=True, y=True)  # 把X和Y的表格打开
        p5.setRange(xRange=[0, historyLength], yRange=[0, 255], padding=0)
        p5.setLabel(axis='left', text='y / V')  # 靠左
        p5.setLabel(axis='bottom', text='x 0.1s')
        p5.setTitle('DAW - p5')  # 表格的名字
        curve2 = p5.plot()  # 绘制一个图形
        curve2.setData(data)
        self.gridLayout.addWidget(p5, 1, 2, 1, 1)
    def linePlot6(self):
        p6.showGrid(x=True, y=True)  # 把X和Y的表格打开
        p6.setRange(xRange=[0, historyLength], yRange=[0, 255], padding=0)
        p6.setLabel(axis='left', text='y / V')  # 靠左
        p6.setLabel(axis='bottom', text='x 0.1s')
        p6.setTitle('DAW - p6')  # 表格的名字
        curve2 = p6.plot()  # 绘制一个图形
        curve2.setData(data)
        self.gridLayout.addWidget(p6, 2, 2, 1, 1)
def plotData():  
    global i,currentLength,Start_record,data_update,first_data_update

    if Start_record:
        i = i + 1
        #print(i)
        if i > historyLength:
            currentLength = currentLength + 1
        if data_update == False:# make sure X is time 
            if first_data_update:
                data1.append(data1[-1])#data1[-1]
                data2.append(data2[-1])
                data3.append(data3[-1])
                data4.append(data4[-1])
                data5.append(data5[-1])
                data6.append(data6[-1])
                print(i)
            else:
                data1.append(0)#data1[-1]
                data2.append(0)
                data3.append(0)
                data4.append(0)
                data5.append(0)
                data6.append(0)
                #print(i)
        data_update = False
        p1.setRange(xRange=[0, currentLength], yRange=[0, 255], padding=0)
        curve1 = p1.plot(pen = 'y')  # 绘制一个图形P1
        curve1.setData(data1)
        p2.setRange(xRange=[0, currentLength], yRange=[0, 255], padding=0)
        curve2 = p2.plot()  # 绘制一个图形P2
        curve2.setData(data2)    
        p3.setRange(xRange=[0, currentLength], yRange=[0, 255], padding=0)
        curve3 = p3.plot()  # 绘制一个图形P3
        curve3.setData(data3)
        p4.setRange(xRange=[0, currentLength], yRange=[0, 255], padding=0)
        curve4 = p4.plot()  # 绘制一个图形P4
        curve4.setData(data4)   
        p5.setRange(xRange=[0, currentLength], yRange=[0, 255], padding=0)
        curve5 = p5.plot()  # 绘制一个图形P5
        curve5.setData(data5)
        p6.setRange(xRange=[0, currentLength], yRange=[0, 255], padding=0)
        curve6 = p6.plot()  # 绘制一个图形P6
        curve6.setData(data6)       
if __name__ == '__main__':
    data = array.array('i')  # 可动态改变数组的大小,int型数组
    mSerial = serial.Serial('COM3', 115200)
    print('serial port open successfully ')
    #config_uart()
    app = QApplication(sys.argv)
    p1 = pg.PlotWidget()
    p2 = pg.PlotWidget()
    p3 = pg.PlotWidget()
    p4 = pg.PlotWidget()
    p5 = pg.PlotWidget()
    p6 = pg.PlotWidget()
    
    data1 = array.array('i')  # 可动态改变数组的大小,int型数组
    data2 = array.array('i')  # 可动态改变数组的大小,int型数组
    data3 = array.array('i')  # 可动态改变数组的大小,int型数组
    data4 = array.array('i')  # 可动态改变数组的大小,int型数组
    data5 = array.array('i')  # 可动态改变数组的大小,int型数组
    data6 = array.array('i')  # 可动态改变数组的大小,int型数组
    
    DAW = DebugAnalysisWave()
    DAW.show()
    th1 = threading.Thread(target=Serial)#create a thread for uart receive
    th1.start()
    timer = pg.QtCore.QTimer()
    timer.timeout.connect(plotData )  # 定时刷新数据显示 plotData
    timer.start(sampling_time)  # 多少ms调用一次
    sys.exit(app.exec_())