# coding=utf-8
import sys
from unittest import TestCase, main
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


class TestReadDataFromTerminal(TestCase):

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
        argumentsDict = misc.no_arguments()

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
            argumentsDict = misc.read_arguments(testargs)

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
        testargs = ["client_amp.py", "-s", "-f", ".settings", "-l", "DEBUG"]
        with patch.object(sys, 'argv', testargs):
            arguments_dict = misc.read_arguments(testargs)

        return self.assertIs(arguments_dict['file'], '.settings'), \
               self.assertIs(arguments_dict['log_level'], 'DEBUG')


class TestSelectReadingArgumentsMethod(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # TODO Complete description
    def test_read_arguments_from_terminal(self):
        """ Reads arguments by terminal test method.
        Tries to read a

        @return: An assertEqual statement
        """
        misc.read_arguments = MagicMock(return_value=True)

        test_args = ["client_amp.py", "-g"]
        with patch.object(sys, 'argv', test_args):
            misc.check_arguments(test_args)

        return self.assertEqual(int(misc.read_arguments.call_count), 1)

    # TODO Complete description
    def test_read_settings_from_terminal(self):
        """

        @return:
        """
        misc.read_arguments = MagicMock(return_value=True)

        test_args = ["client_amp.py", "-s"]
        with patch.object(sys, 'argv', test_args):
            misc.read_arguments(test_args)

        return self.assertEqual(misc.read_arguments.call_count, 1)

    # TODO Complete description
    def test_option_not_valid(self):
        """

        @return:
        """
        test_args = ["client_amp.py", "-l"]
        with patch.object(sys, 'argv', test_args):
            arguments_dict = misc.check_arguments(test_args)

        return self.assertIsNone(arguments_dict)

    # TODO Complete description
    def test_option_not_given(self):
        """

        @return:
        """
        misc.no_arguments = MagicMock(return_value=True)

        test_args = ["client_amp.py"]
        with patch.object(sys, 'argv', test_args):
            misc.check_arguments(test_args)

        return self.assertEqual(misc.no_arguments.call_count, 1)

if __name__ == "__main__":
    main()