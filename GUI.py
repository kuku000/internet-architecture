import sys
import os
#import cv2
import time
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtGui import *
import PyQt5.QtCore
from PyQt5.QtCore import Qt, QRegExp, QEventLoop,QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QGraphicsView, QGraphicsScene, QFileDialog, QGroupBox, QPushButton, QLineEdit, QSpinBox, QStackedLayout, QLabel, QGridLayout, QInputDialog
from PyQt5.QtGui import QPainter, QPixmap, QColor
import socket
import select
import errno
import sys

import argparse

#宣告視窗
class MyWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.init_ui()
    def break_loop(self):
        # 每次計時器觸發時，更新標籤內容
        self.loop.quit()
        #print("掃描")
    def init_ui(self):
        
        self.save_massege_box = []
        self.setWindowTitle("網際網路聊天室")
        self.setGeometry(400, 50, 800, 800)
        self.user_name = ""
        self.loop = QEventLoop()
        self.send_this = ""
        self.break_flag = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.break_loop)
        self.timer.start(100)  # 啟動計時器，指定時間間隔
        font = PyQt5.QtGui.QFont()
        #font.setFamily('Verdana')
        font.setPointSize(14)
        

        
        
        self.folder_path5_0 = ""

        layout = QGridLayout()

        #region
        # 第0題設定
        zero_box = QGroupBox("聊天室")
        
        zero_box.setFont(font)
        #0000FF
        zero_box.setFixedSize(600,600)
        
        zero_box_layout = QGridLayout()
        self.label0 = QLabel()
        self.label0.setFixedSize(550,550)
        self.label0.setAlignment(PyQt5.QtCore.Qt.AlignmentFlag.AlignLeft)
        self.label0.setFont(font)
        self.label0.setWordWrap(True)
        
        zero_box_layout.addWidget(self.label0,0,0)
        
        zero_box.setLayout(zero_box_layout)

        one_box = QGroupBox("在這邊輸入")
        one_box.setFont(font)
        one_box.setFixedSize(600,200)
        self.lineedit1 = QLineEdit()
        self.lineedit1.setFixedSize(500,100)
        one_box_layout = QGridLayout()
        one_box_layout.addWidget(self.lineedit1,0,0)
        one_box.setLayout(one_box_layout)


        two_box = QGroupBox()
        two_box.setFixedSize(200,200)
        two_box_layout = QGridLayout()
        self.btn2_1 = QPushButton("傳送")
        self.btn2_2 = QPushButton("玩遊戲")
        self.btn2_3 = QPushButton("結束對話")
        self.btn2_1.setFont(font)
        self.btn2_2.setFont(font)
        self.btn2_3.setFont(font)
        two_box_layout.addWidget(self.btn2_1,0,0)
        two_box_layout.addWidget(self.btn2_2,1,0)
        two_box_layout.addWidget(self.btn2_3,2,0)
        two_box.setLayout(two_box_layout)
        
        
        
        


        # #最後安排網格
        layout.setSpacing(30)
        layout.addWidget(zero_box, 0, 0)
        layout.addWidget(one_box, 1, 0)
        layout.addWidget(two_box, 1, 1)
        self.setLayout(layout)   
        #endregion

#設定按鈕連結
def Send_message():
    
    new_message = w.lineedit1.text()
    if not new_message == "":
        w.send_this = new_message
        w.lineedit1.clear()
    w.loop.quit()
    

def Print_in_GUI(w):
    while len(w.save_massege_box) > 17:
        w.save_massege_box.pop(0)
    ready_to_print = ""
    for history in w.save_massege_box:
        ready_to_print += history
        ready_to_print += "\n"
    w.label0.setText(ready_to_print)
    #print(w.Q3_image_path)

def Start_game_flag():

    w.send_this= "game"
    w.loop.quit()

def Quit():
    w.save_massege_box.append("對話結束，請放心關閉本視窗")
    Print_in_GUI(w)
    w.timer.stop()
    w.break_flag=True
    w.loop.quit()
    
def set_button(w):
    w.btn2_1.clicked.connect(Send_message)
    w.btn2_2.clicked.connect(Start_game_flag)
    w.btn2_3.clicked.connect(Quit)
    

    

#顯示視窗
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    w = MyWindow()
    set_button(w)
    w.show()

    count = 1
    HEADER_LENGTH = 10

    IP = '172.20.10.13'
    PORT = 9999
    
    while True:
        
        text, ok = QInputDialog.getText(w, '提示框', '請輸入使用者名稱')
        
        if ok and not text == "":
            w.user_name = text
            break
    my_username = w.user_name
    #print(my_username)
    w.save_massege_box.append(f'歡迎{my_username}的加入，開始享受聊天吧')
    Print_in_GUI(w)
    # Create a socket
    # socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
    # socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to a given ip and port
    client_socket.connect((IP, PORT))

    # Set connection to non-blocking state, so .recv() call won;t block, just return some exception we'll handle
    client_socket.setblocking(False)

    # Prepare username and header and send them
    # We need to encode username to bytes, then count number of bytes and prepare header of fixed size, that we encode to bytes as well
    username = my_username.encode('utf-8')
    username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(username_header + username)


    while True:
        
        # Wait for user to input a message
        #message = False
        #text, ok = QInputDialog.getText(w, '', '')
        
        
        w.loop.exec_()
        if w.break_flag:
            break
        message = w.send_this
        w.send_this = ""
        if not message == "":
            w.save_massege_box.append(f'[you] -----> {message}')
            Print_in_GUI(w)
        
        
        # If message is not empty - send it
        if message:

            # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
            message = message.encode('utf-8')
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
            client_socket.send(message_header + message)

        try:
            # Now we want to loop over received messages (there might be more than one) and print them
            while True:

                # Receive our "header" containing username length, it's size is defined and constant
                username_header = client_socket.recv(HEADER_LENGTH)

                # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
                if not len(username_header):
                    w.save_massege_box.append('Connection closed by the server')
                    Print_in_GUI(w)
                    sys.exit()

                # Convert header to int value
                username_length = int(username_header.decode('utf-8').strip())

                # Receive and decode username
                username = client_socket.recv(username_length).decode('utf-8')

                # Now do the same for message (as we received username, we received whole message, there's no need to check if it has any length)
                message_header = client_socket.recv(HEADER_LENGTH)
                message_length = int(message_header.decode('utf-8').strip())
                message = client_socket.recv(message_length).decode('utf-8')

                # Print message
                w.save_massege_box.append("[" + str(count).zfill(3) + "] " + f'{username} > {message}')
                Print_in_GUI(w)
                count += 1
                if count >= 999:#reset
                    count = 1
    
        except IOError as e:
            # This is normal on non blocking connections - when there are no incoming data error is going to be raised
            # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
            # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
            # If we got different error code - something happened
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                w.save_massege_box.append('Reading error: {}'.format(str(e)))
                Print_in_GUI(w)
                sys.exit()

            # We just did not receive anything
            continue

        except Exception as e:
            # Any other exception - something happened, exit
            w.save_massege_box.append('Reading error: '.format(str(e)))
            Print_in_GUI(w)
            sys.exit()
        
    app.exec()