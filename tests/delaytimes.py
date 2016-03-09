# coding=utf-8
import socket
import threading
import time


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


class Receiveudpframe(threading.Thread):
    def __init__(self, ipreceptor, portreceptor, repetitions):
        super(Receiveudpframe, self).__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ipreceptor = ipreceptor
        self.portreceptor = portreceptor
        self.times = []
        self.repetitions = repetitions

    def run(self):
        self.sock.bind((self.ipreceptor, self.portreceptor))
        while True:
            data, addr = self.sock.recvfrom(1024)
            self.times.append(str(time.time()))
            if len(self.times) == self.repetitions:
                break

class Sendudpframe(threading.Thread):
    def __init__(self, ipsender, portsender, repetitions, delaytime):
        super(Sendudpframe, self).__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ipsender = ipsender
        self.portsender = portsender
        self.times = []
        self.repetitions = repetitions
        self.delaytime = delaytime

    def run(self):
        for i in range(0, self.repetitions, 1):
            message = bytearray('Test message')
            self.sock.sendto(message, (self.ipsender, self.portsender))
            self.times.append(str(time.time()))

            time.sleep(self.delaytime)


if __name__=='__main__':
    """
    Parameters useful for the test operation.
    """
    ipsender = '127.0.0.1'
    portsender = 57008
    ipreceptor = ''
    portreceptor = 57009

    repetitions = 50
    delaytime = 1

    udpsendthread = Sendudpframe(ipsender, portsender, repetitions, delaytime)
    udpsendthread.start()
    udpreceivethread = Receiveudpframe(ipreceptor, portreceptor, repetitions)
    udpreceivethread.start()

    udpsendthread.join()
    udpreceivethread.join()

    delays = []
    if len(udpreceivethread.times) == len(udpsendthread.times):
        print "No packets lost. Perfoming tests."
        for i in range(len(udpreceivethread.times)):
            delay = float(udpreceivethread.times[i]) - \
                    float(udpsendthread.times[i])
            delays.append(delay)

    import statistics
    print "Minimum delay", (min(delays))
    print "Maximum delay", (max(delays))
    print "Mean delay", (statistics.mean(delays))
    print "Median delay", (statistics.median(delays))