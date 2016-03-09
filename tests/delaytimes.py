# coding=utf-8
import os
import sys
import socket
import threading
import datetime
import time

from time import sleep


"""
   Copyright 2016 Samuel Góngora García
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
:Author:
    Samuel Góngora García (s.gongoragarcia@gmail.com)
"""
__author__ = 's.gongoragarcia@gmail.com'


# send package through ip, port
# receive package through ip, port


class Receiveudpframe(threading.Thread):
    def __init__(self, ipreceptor, portreceptor):
        super(Receiveudpframe, self).__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ipreceptor = ipreceptor
        self.portreceptor = portreceptor
        self.times = []

    def run(self):
        self.sock.bind((self.ipreceptor, self.portreceptor))
        timeout = time.time() + 20
        while True:
            data, addr = self.sock.recvfrom(1024)

            data = bytearray(data)
            print data, str(time.time())

            self.times.append(str(time.time()))

            if time.time() > timeout:
                break

class Sendudpframe(threading.Thread):
    def __init__(self, ipsender, portsender):
        super(Sendudpframe, self).__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ipsender = ipsender
        self.portsender = portsender

    def run(self):
        for i in range(0, 20, 1):

            message = bytearray('patata')
            print message
            self.sock.sendto(message, (self.ipsender, self.portsender))
            sleep(1)
            e = str(i)
            print "send %s at %s" %(message, str(time.time()))


if __name__=='__main__':
    """
    ipsender = str(sys.argv[1])
    portsender = int(sys.argv[2])
    ipreceptor = str(sys.argv[3])
    portreceptor = int(sys.argv[4])
    """

    ipsender = '127.0.0.1'
    portsender = 57008
    ipreceptor = ''
    portreceptor = 57009

    udpsendthread = Sendudpframe(ipsender, portsender)
    udpsendthread.start()
    udpreceivethread = Receiveudpframe(ipreceptor, portreceptor)
    udpreceivethread.start()

    udpsendthread.join()
    udpreceivethread.join()

    print udpreceivethread.times