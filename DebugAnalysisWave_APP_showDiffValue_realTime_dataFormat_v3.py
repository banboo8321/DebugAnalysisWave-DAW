from PyQt5.QtWidgets import QPushButton,QWidget,QApplication,QGridLayout,QListWidget,QLineEdit
import pyqtgraph as pg
import sys
import array
import serial
import threading
import numpy as np
import time
from queue import Queue
import re
#    debug_name = 'DAW_debug_name:DAW_1;DAW_2;DAW_3;DAW_4;DAW_5;DAW_6_test\n'
#    byte_line = 'DAW_frame:10;255;256;300;1000;10000\n'  DAW_frame:1;2;256;200;10;100
#DAW_debug_name:DAW_test_1;DAW_t2;DAW_t3;DAW_t4;DAW_t5;DAW_t6_test


data_dict = {}#存放所有收到的数据
      
sampling_time = 100
i = 0
historyLength = 100  # 横坐标长度 time: n second = 10 ms * n00
currentLength = historyLength
Start_record = False
data_update = False
first_data_update = False

def config_uart():
    # User input comport and bundrate
    #comport = 'COM3'
    #baudrate = 115200
    #parity_input ='1'
    comport = input('Please input comport (like COM3) for your connected device: ')
    baudrate = input('Please input baudrate (like 9600) for your connected device: ')
    parity_input = input('Please input parity (like 0:None,1:ODD,2:EVEN) for your connected device: ')
    if parity_input =='0':
        parity_in = serial.PARITY_NONE
        print('Selected PARITY_NONE')
    elif parity_input =='1':
        parity_in = serial.PARITY_ODD
        print('Selected PARITY_ODD')
    elif parity_input =='2':
        parity_in = serial.PARITY_EVEN
        print('Selected PARITY_EVEN')
    else:
        parity_in = serial.PARITY_NONE
        #parity_input = input('Out of range! Please input parity (like 0:None,1:ODD,2:EVEN) for your connected device: ')
    print('You selected %s, baudrate %d.' % (comport, int(baudrate)))
        # 串口执行到这已经打开 再用open命令会报错
    s = serial.Serial(comport, int(baudrate),parity = parity_in)
    if (s.isOpen()):
        print("open uart success")
        s.write("hello DAW\r\n".encode()) # 向端口些数据 字符串必须译码
        s.flushInput()  # 清空缓冲区
        return s
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

   # debug_name = 'DAW_debug_name:DAW_1;DAW_2;DAW_3;DAW_4;DAW_5;DAW_6\n'
def AddNameToDict(line):
    line = line.split("DAW_debug_name:") #目的是去除DAW_debug_name:换行
    print(line)#'DAW_debug_name:','DAW_1;DAW_2;DAW_3;DAW_4;DAW_5;DAW_6\n'
    str_line = line[1].split("\n") #目的是去除最后的\n换行
    print(str_line)#'DAW_1;DAW_2;DAW_3;DAW_4;DAW_5;DAW_6'
    str_arr = str_line[0].split(';')#因为上边分割了一下，所以是数组
    print(str_arr)#'DAW_1',DAW_2',DAW_3',DAW_4',DAW_5','DAW_6'
    #color = ['b','g','r', 'c','m','y', 'k','w']#颜色表，这些应该够了，最多8条线，在添加颜色可以用(r,g,b)表示
    print(str_arr[0])
    print(str_arr[5])
    p1.setTitle(str_arr[0])  # 表格的名字
    p2.setTitle(str_arr[1])  # 表格的名字
    p3.setTitle(str_arr[2])  # 表格的名字
    p4.setTitle(str_arr[3])  # 表格的名字
    p5.setTitle(str_arr[4])  # 表格的名字
    p6.setTitle(str_arr[5])  # 表格的名字
 
   # byte_line1 = 'DAW_frame:1;2;3;4;5;6\n'       
def AddDataToDict(line):
    global Start_record,data_update,first_data_update
    if Start_record:
        line = line.split("DAW_frame:") #目的是去除最后的\n换行，别的方式还没用明白
        #print(line) #'DAW_frame:','1;2;3;4;5;6\n'
        str_line = line[1].split("\n") #目的是去除最后的\n换行，别的方式还没用明白
        #print(str_line)#'1;2;3;4;5;6'
        str_arr = str_line[0].split(';')#因为上边分割了一下，所以是数组
        #print(str_arr)#'1','2'...,'6'

        #int_arr = int(str_arr)
        #print("int_arr",int_arr)
        #for a in str_arr: #遍历获取单个变量 如“a,1;b,2;c,3”中的"a,1"
        #    s = a.split(',')#提取名称和数据部分
        #    print(s)
        if len(str_arr) == 6:#'1','2'...,'6'
        #if(checksum(int_arr) == True): #receive a correct package data
            #print(str_arr[0])
            data1.append(int(str_arr[0]))
            data2.append(int(str_arr[1]))
            data3.append(int(str_arr[2]))
            data4.append(int(str_arr[3]))
            data5.append(int(str_arr[4]))
            data6.append(int(str_arr[5]))
            #print(str_arr[5])
            data_update = True
            first_data_update = True
        #if(len(s) != 2):#不等于2字符串可能错了，正确的只有名称和数据两个字符串
        #    return

        
 
def Serial():
    while(True):
        while mSerial.isOpen():
            try:
                #print("waiting for connect data ...")
                if mSerial.inWaiting():
                    #data_r = int.from_bytes(mSerial.readline(1),byteorder='little')  
                    line = mSerial.readline().decode() #line是bytes格式，使用decode()转成字符串
                    #print(line)
                    if(line.startswith( 'DAW_frame:' )):
                        AddDataToDict(line)
                    elif(line.startswith( 'DAW_debug_name:' )):
                        AddNameToDict(line)
                    #global Start_record,data_update,first_data_update
                    #
                    #
                    #
                    #if Start_record:
                    #    data.append(data_r)
                    #    if data_r == 10 :#0x0A
                    #        if(checksum(data[-6]) == True): #receive a correct package data
                    #            #print('start convert data1')
                    #            data1.append(data[-6])
                    #            data2.append(data[-5])
                    #            data3.append(data[-4])
                    #            data4.append(data[-3])
                    #            data5.append(data[-2])
                    #            data6.append(data[-1])
                    #            #print('data3',data3)
                    #            data_update = True
                    #            first_data_update = True
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
        curve1 = p1.plot(pen = 'b')  # 绘制一个图形
        curve1.setData(data)
        self.gridLayout.addWidget(p1, 0, 1, 1, 1)
    def linePlot2(self):
        p2.showGrid(x=True, y=True)  # 把X和Y的表格打开
        p2.setRange(xRange=[0, historyLength], yRange=[0, 255], padding=0)
        p2.setLabel(axis='left', text='y / V')  # 靠左
        p2.setLabel(axis='bottom', text='x 0.1s')
        p2.setTitle('DAW - p2')  # 表格的名字
        curve2 = p2.plot(pen = 'g')  # 绘制一个图形
        curve2.setData(data)
        self.gridLayout.addWidget(p2, 1, 1, 1, 1)
    def linePlot3(self):
        p3.showGrid(x=True, y=True)  # 把X和Y的表格打开
        p3.setRange(xRange=[0, historyLength], yRange=[0, 255], padding=0)
        p3.setLabel(axis='left', text='y / V')  # 靠左
        p3.setLabel(axis='bottom', text='x 0.1s')
        p3.setTitle('DAW - p3')  # 表格的名字
        curve2 = p3.plot(pen = 'r')  # 绘制一个图形
        curve2.setData(data)
        self.gridLayout.addWidget(p3, 2, 1, 1, 1)
    def linePlot4(self):
        p4.showGrid(x=True, y=True)  # 把X和Y的表格打开
        p4.setRange(xRange=[0, historyLength], yRange=[0, 255], padding=0)
        p4.setLabel(axis='left', text='y / V')  # 靠左
        p4.setLabel(axis='bottom', text='x 0.1s')
        p4.setTitle('DAW - p4')  # 表格的名字
        curve2 = p4.plot(pen = 'c')  # 绘制一个图形
        curve2.setData(data)
        self.gridLayout.addWidget(p4, 0, 2, 1, 1)
    def linePlot5(self):
        p5.showGrid(x=True, y=True)  # 把X和Y的表格打开
        p5.setRange(xRange=[0, historyLength], yRange=[0, 255], padding=0)
        p5.setLabel(axis='left', text='y / V')  # 靠左
        p5.setLabel(axis='bottom', text='x 0.1s')
        p5.setTitle('DAW - p5')  # 表格的名字
        curve2 = p5.plot(pen = 'm')  # 绘制一个图形
        curve2.setData(data)
        self.gridLayout.addWidget(p5, 1, 2, 1, 1)
    def linePlot6(self):
        p6.showGrid(x=True, y=True)  # 把X和Y的表格打开
        p6.setRange(xRange=[0, historyLength], yRange=[0, 255], padding=0)
        p6.setLabel(axis='left', text='y / V')  # 靠左
        p6.setLabel(axis='bottom', text='x 0.1s')
        p6.setTitle('DAW - p6')  # 表格的名字
        curve2 = p6.plot(pen = 'y')  # 绘制一个图形
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
                #print(i)
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
        curve1 = p1.plot(pen = 'g')  # 绘制一个图形P1
        curve1.setData(data1)
        p2.setRange(xRange=[0, currentLength], yRange=[0, 255], padding=0)
        curve2 = p2.plot(pen = 'r')  # 绘制一个图形P2
        curve2.setData(data2)    
        p3.setRange(xRange=[0, currentLength], yRange=[0, 255], padding=0)
        curve3 = p3.plot(pen = 'y')  # 绘制一个图形P3
        curve3.setData(data3)
        p4.setRange(xRange=[0, currentLength], yRange=[0, 255], padding=0)
        curve4 = p4.plot(pen = 'b')  # 绘制一个图形P4
        curve4.setData(data4)   
        p5.setRange(xRange=[0, currentLength], yRange=[0, 255], padding=0)
        curve5 = p5.plot(pen = 'c')  # 绘制一个图形P5
        curve5.setData(data5)
        p6.setRange(xRange=[0, currentLength], yRange=[0, 255], padding=0)
        curve6 = p6.plot(pen = 'm')  # 绘制一个图形P6
        curve6.setData(data6)
        

if __name__ == '__main__':
    data = array.array('i')  # 可动态改变数组的大小,int型数组
    mSerial = config_uart()#serial.Serial('COM3', 115200,parity=serial.PARITY_ODD)
    #mSerial.parity=serial.PARITY_NONE
    #if(mSerial.isOpen() == True):      
    #    mSerial.flushInput() #先清空一下缓冲区
    #    print('serial port open successfully ')
    #config_uart()
    app = QApplication(sys.argv)
    p1 = pg.PlotWidget()
    p2 = pg.PlotWidget()
    p3 = pg.PlotWidget()
    p4 = pg.PlotWidget()
    p5 = pg.PlotWidget()
    p6 = pg.PlotWidget()
    #p1.addLegend() #不添加就显示不了图例 ，一定要放在plot前调用
    
    data1 = array.array('i')  # 可动态改变数组的大小,int型数组
    data2 = array.array('i')  # 可动态改变数组的大小,int型数组
    data3 = array.array('i')  # 可动态改变数组的大小,int型数组
    data4 = array.array('i')  # 可动态改变数组的大小,int型数组
    data5 = array.array('i')  # 可动态改变数组的大小,int型数组
    data6 = array.array('i')  # 可动态改变数组的大小,int型数组

    
    DAW = DebugAnalysisWave()
    DAW.show()
    #debug_name = 'DAW_debug_name:DAW_1;DAW_2;DAW_3;DAW_4;DAW_5;DAW_6_test\n'
    #byte_line = 'DAW_frame:10;255;256;300;1000;10000\n'
    #AddNameToDict(debug_name)
    #AddDataToDict(byte_line)
    th1 = threading.Thread(target=Serial)#create a thread for uart receive
    th1.start()
    timer = pg.QtCore.QTimer()
    timer.timeout.connect(plotData )  # 定时刷新数据显示 plotData
    timer.start(sampling_time)  # 多少ms调用一次
    sys.exit(app.exec_())