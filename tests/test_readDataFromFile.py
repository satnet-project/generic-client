# coding=utf-8
import os
import sys

from twisted.python import log
from twisted.trial.unittest import TestCase

# Errors
from ConfigParser import NoSectionError
from exceptions import KeyError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                "..")))
import misc

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


class TestReadDataFromFile(TestCase):

    def setUp(self):
        testFile = open(".settings", "w")
        testFile.write("[User]\n"
                       "username = test-sc-user\n"
                       "password = sgongarpass\n"
                       "slot_id = -1\n"
                       "connection = none\n"
                       "\n"
                       "[Serial]\n"
                       "serialport = /dev/ttyUSB0\n"
                       "baudrate = 500000\n"
                       "\n"
                       "[udp]\n"
                       "udpipreceive = 127.0.0.1\n"
                       "udpportreceive = 1234\n"
                       "udpipsend = 172.19.51.145\n"
                       "udpportsend = 57009\n"
                       "\n"
                       "[tcp]\n"
                       "tcpipreceive = 127.0.0.1\n"
                       "tcpportreceive = 4321\n"
                       "tcpipsend = 127.0.0.1\n"
                       "tcpportsend = 1234\n"
                       "\n"
                       "[server]\n"
                       "serverip = 172.19.51.133\n"
                       "serverport = 25345\n"
                       "\n"
                       "[Connection]\n"
                       "reconnection = no\n"
                       "parameters = yes\n"
                       "\n"
                       "[Client]\n"
                       "name = Universidade de Vigo\n"
                       "attempts = 10")
        testFile.close()

    def tearDown(self):
        os.remove(".settings")

    """
    Proper file.
    """
    def test_loadRightFile(self):
        argumentsDict = misc.get_data_local_file('.settings')
        return self.assertIsInstance(argumentsDict, dict)

    """
    Wrong file.
    """
    def test_loadWrongFile(self):
        return self.assertRaises(NoSectionError, misc.get_data_local_file,
                                 'wrongFile')
    """
    Proper key.
    """
    def test_loadRightKey(self):
        argumentsDict = misc.get_data_local_file('.settings')
        return self.assertIsInstance(argumentsDict['serverip'], str)

    """
    Wrong key.
    """
    def test_loadWrongKey(self):
        argumentsDict = misc.get_data_local_file('.settings')
        return self.assertRaises(KeyError, lambda: argumentsDict['wrongKey'])
