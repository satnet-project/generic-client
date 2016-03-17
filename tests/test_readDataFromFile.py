# coding=utf-8
import os
import sys

from twisted.trial.unittest import TestCase
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

    def create_settings_file(self):
        """ Create settings file.
        Create a settings file for tests purposes.

        @return: Nothing.
        """
        test_file = open(".settings", "w")
        test_file.write("[User]\n"
                        "institution = Universidade de Vigo\n"
                        "username = test-user-sc\n"
                        "password = pass\n"
                        "slot_id = -1\n"
                        "connection = udp\n"
                        "\n"
                        "[Serial]\n"
                        "serialport = /dev/ttyUSB0\n"
                        "baudrate = 500000\n"
                        "\n"
                        "[udp]\n"
                        "udpipreceive = 127.0.0.1\n"
                        "udpportreceive = 57109\n"
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
                        "serverip = 127.0.0.1\n"
                        "serverport = 25345\n"
                        "\n"
                        "[Connection]\n"
                        "reconnection = yes\n"
                        "parameters = no\n"
                        "attempts = 10\n")
        test_file.close()

    def setUp(self):
        self.create_settings_file()

    def tearDown(self):
        """ Tear down method.
        Between each test the settings configuration file must be remove.
        @return: Nothing.
        """
        os.remove(".settings")

    def test_load_right_file(self):
        """ Loads right file.
        Tries to load the configuration from the settings file.

        @return: An assertIsInstance method which checks that the object
        returned is a dict.
        """
        argumentsDict = misc.get_data_local_file('.settings')
        return self.assertIsInstance(argumentsDict, dict)

    def test_load_wrong_file(self):
        """ Loads wrong file.

        @return: An assertRaises method which checks that the function
        called raises a NoSectionError.
        """
        return self.assertRaises(NoSectionError, misc.get_data_local_file,
                                 'wrongFile')

    def test_load_right_key_from_right_file(self):
        """ Loads right key from settings file.
        Loads a rightful settings dictionary. Then tries to load
        a right key.

        @return: An assertIsInstance method which checks that the loaded
        value is a string.
        """
        argumentsDict = misc.get_data_local_file('.settings')
        return self.assertIsInstance(argumentsDict['serverip'], str)

    def test_load_wrong_key_from_right_file(self):
        """ Loads wrong key from settings dictionary.
        Tries to load a wrong key from a correct settings dictionary.

        @return: An assertRaises method which checks that the function
        called raises a KeyError.
        """
        argumentsDict = misc.get_data_local_file('.settings')
        return self.assertRaises(KeyError, lambda: argumentsDict['wrongKey'])
