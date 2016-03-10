# coding=utf-8
import unittest
import sys

from os import path
from mock import patch, Mock, MagicMock

sys.path.append(path.abspath(path.join(path.dirname(__file__), "..")))
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


class TestReadDataFromTerminal(unittest.TestCase):

    def setUp(self):
        pass

    def teardrown(self):
        pass

    def test_no_arguments_given(self):
        """ No arguments passed by terminal.
        If no argument has been pass using the terminal every parameter
        are going to be empty.
        Through a for structure this test checks this affirmation.

        @return: A true boolean if there is no error.
        """
        argumentsDict = misc.noArguments()

        arguments = ['username', 'slot', 'connection', 'serialport', 'baudrate',
                     'udpipsend', 'udpportsend', 'udpipreceive', 'udpportreceive']
        for i in range(len(arguments)):
            self.assertEquals(argumentsDict[arguments[i]],
                              '', "argumentsDict values are not null.")
        return True

    # TODO Complete description
    def test_arguments_given(self):
        """ Arguments passed by terminal.

        @return: A true bolean if there is no error.
        """
        testargs = ["client_amp.py", "-g", "-n", "crespo", "-t",
                    "2", "-c", "serial", "-s", "/dev/ttyS1",
                    "-b", "115200"]
        with patch.object(sys, 'argv', testargs):
            argumentsDict = misc.readArguments(testargs)

        descriptors = ['username', 'slot', 'baudrate', 'serialport',
                       'connection']

        for i in range(len(descriptors)):
            self.assertIsInstance(argumentsDict[(descriptors[i])], str,
                                  "Dict value is not a string object")

        return True

    # TODO Complete description
    def test_file_allocation_given(self):
        """ Settings file allocation given.

        @return: An assertIs method which checks the value of the dictionary
        created.
        """
        testargs = ["client_amp.py", "-s", "-f", ".settings"]
        with patch.object(sys, 'argv', testargs):
            arguments_dict = misc.readSettings(testargs)

        return self.assertIs(arguments_dict['file'], '.settings')

class TestSelectReadingArgumentsMethod(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # TODO Complete description
    def test_read_arguments_from_terminal(self):
        """

        @return:
        """
        misc.readArguments = MagicMock(return_value=True)

        testargs = ["client_amp.py", "-g"]
        with patch.object(sys, 'argv', testargs):
            arguments_dict = misc.checkarguments(testargs)

        return self.assertEqual(int(misc.readArguments.call_count), 1)

    # TODO Complete description
    def test_read_settings_from_terminal(self):
        """

        @return:
        """
        misc.readSettings = MagicMock(return_value=True)

        testargs = ["client_amp.py", "-s"]
        with patch.object(sys, 'argv', testargs):
            arguments_dict = misc.checkarguments(testargs)

        return self.assertEqual(misc.readSettings.call_count, 1)

    # TODO Complete description
    def test_option_not_valid(self):
        """

        @return:
        """
        testargs = ["client_amp.py", "-l"]
        with patch.object(sys, 'argv', testargs):
            arguments_dict = misc.checkarguments(testargs)

        return self.assertIsNone(arguments_dict)

    # TODO Complete description
    def test_option_not_given(self):
        """

        @return:
        """
        misc.noArguments = MagicMock(return_value=True)

        testargs = ["client_amp.py"]
        with patch.object(sys, 'argv', testargs):
            arguments_dict = misc.checkarguments(testargs)

        return self.assertEqual(misc.noArguments.call_count, 1)