# coding=utf-8
import datetime
import pytz
import getopt

from twisted.python import log
from errors import ArgumentsInvalid

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


def get_now_utc(no_microseconds=True):
    """
    This method returns now's datetime object UTC localized.
    :param no_microseconds: sets whether microseconds should be cleared.
    :return: the just created datetime object with today's date.
    """
    if no_microseconds:
        return pytz.utc.localize(datetime.datetime.utcnow()).replace(
            microsecond=0
        )
    else:
        return pytz.utc.localize(datetime.datetime.utcnow())


def localize_date_utc(date):
    """
    Localizes in the UTC timezone the given date object.
    :param date: The date object to be localized.
    :return: A localized datetime object in the UTC timezone.
    """
    return pytz.utc.localize(
        datetime.datetime.combine(
            date, datetime.time(hour=0, minute=0, second=0)
        )
    )


def localize_datetime_utc(date_time):
    """
    Localizes in the UTC timezone a given Datetime object.
    :param date_time: The object to be localized.
    :return: Localized Datetime object in the UTC timezone.
    """
    return pytz.utc.localize(date_time)


def localize_time_utc(non_utc_time):
    """
    Localizes in the UTC timezone the given time object.
    :param non_utc_time: The time object to be localized.
    :return: A localized time object in the UTC timezone.
    """
    return pytz.utc.localize(non_utc_time)

TIMESTAMP_0 = localize_date_utc(datetime.datetime(year=1970, month=1, day=1))


def get_utc_timestamp(utc_datetime=None):
    """
    Returns a timestamp with the number of microseconds ellapsed since January
    1st of 1970 for the given datetime object, UTC localized.
    :param utc_datetime: The datetime whose timestamp is to be calculated.
    :return: The number of miliseconds since 1.1.1970, UTC localized (integer)
    """
    if utc_datetime is None:
        utc_datetime = get_now_utc()
    diff = utc_datetime - TIMESTAMP_0
    return int(diff.total_seconds() * 10**6)


def no_arguments():
    """ No arguments given function.
    Creates a new empty dictionary with the fields needed.

    @return: arguments_dict. An empty dictionary.
    """
    arguments_dict = {}
    arguments = ['username', 'slot', 'connection',
                 'serialport', 'baudrate', 'udpipsend', 'udpportsend',
                 'udpipreceive', 'udpportreceive']
    for i in range(len(arguments)):
        arguments_dict[arguments[i]] = ''

    return arguments_dict


def read_arguments(arguments_dict):
    """ Reads arguments through terminal.


    @rtype: A dictionary with
    """
    if arguments_dict[1] == '-g':
        try:
            opts, args = getopt.getopt(arguments_dict[1:],
                                       "hfgn:t:c:s:b:is:us:ir:ur",
                                       ["name=",
                                        "slot=", "connection=",
                                        "serialport=",
                                        "baudrate=", "udpipsend=",
                                        "udpportsend=", "udpipreceive=",
                                        "udpportreceive="]
                                       )
        except getopt.GetoptError:
            raise ArgumentsInvalid("Some arguments are no valid.")

        settings_dict = {}
        if ('-g', '') in opts:
            for opt, arg in opts:
                if opt == "-n":
                    settings_dict['username'] = arg
                elif opt == "-t":
                    settings_dict['slot'] = arg
                elif opt == "-c":
                    settings_dict['connection'] = arg
                elif opt == "-s":
                    settings_dict['serialport'] = arg
                elif opt == "-b":
                    settings_dict['baudrate'] = arg
                elif opt == "-is":
                    settings_dict['udpipsend'] = arg
                elif opt == "-us":
                    settings_dict['udpportsend'] = arg
                elif opt == "-ir":
                    settings_dict['udpipreceive'] = arg
                elif opt == "-ur":
                    settings_dict['udpportreceive'] = arg
        return settings_dict

    elif arguments_dict[1] == '-s':
        try:
            opts, args = getopt.getopt(arguments_dict[1:],
                                       "fsf",
                                       ["file="]
                                       )
        except getopt.GetoptError:
            raise ArgumentsInvalid("Some arguments are no valid.")

        settings_dict = {}

        for opt, arg in opts:
            if opt == "-f":
                settings_dict['file'] = args[0]

        return settings_dict


def checkarguments(sysargv_dict):
    """ Checks arguments given by terminal.
    Compares the second value of the list given. If there is no value runs
    no_arguments function.

    @param sysargv_dict: A list containing all the arguments.
    @return: A dictionary of configuration parameters. Nothing if the
    arguments are invalid.
    """
    try:
        if sysargv_dict[1] == "-g":
            settings_dict = read_arguments(sysargv_dict)
            return settings_dict
        elif sysargv_dict[1] == "-s":
            settings_dict = read_arguments(sysargv_dict)
            return settings_dict
        elif sysargv_dict[1] != "-g" and sysargv_dict[1] != "-help":
            log.msg("Unknown option: %s" % (sysargv_dict[1]))
            log.msg("Try 'python client_amp.py -help' for more information.")
            return None
    except IndexError:
        settings_dict = no_arguments()
        return settings_dict


def get_data_local_file(settingsfile):
    """ Gets data from local file.
    Gets configuration settings from local file.

    @param settingsfile: Settings file location.
    @return: A dictionary which contains the connection's data.
    """
    connect_info = {}

    from ConfigParser import ConfigParser
    config = ConfigParser()
    config.read(settingsfile)

    connect_info['reconnection'] = config.get('Connection', 'reconnection')
    connect_info['parameters'] = config.get('Connection', 'parameters')
    connect_info['name'] = config.get('User', 'institution')
    connect_info['attempts'] = config.get('Connection', 'attempts')
    connect_info['username'] = config.get('User', 'username')
    connect_info['connection'] = config.get('User', 'connection')
    connect_info['serialport'] = config.get('Serial', 'serialport')
    connect_info['baudrate'] = config.get('Serial', 'baudrate')
    connect_info['udpipreceive'] = config.get('udp', 'udpipreceive')
    connect_info['udpportreceive'] = int(config.get('udp', 'udpportreceive'))
    connect_info['udpipsend'] = config.get('udp', 'udpipsend')
    connect_info['udpportsend'] = config.get('udp', 'udpportsend')
    connect_info['tcpipreceive'] = config.get('tcp', 'tcpipreceive')
    connect_info['tcpportreceive'] = int(config.get('tcp', 'tcpportreceive'))
    connect_info['tcpipsend'] = config.get('tcp', 'tcpipsend')
    connect_info['tcpportsend'] = config.get('tcp', 'tcpportsend')
    connect_info['serverip'] = config.get('server', 'serverip')
    connect_info['serverport'] = int(config.get('server', 'serverport'))

    return connect_info


def set_data_local_file(settingsfile, connect_info):
    """ Sets data to local file.
    Compares reconnection and parameters field and it changes them in the
    settings file if there is any difference.

    @param settingsfile: Settings file location.
    @param connect_info: Settings dictionary.
    @return: True if everything is alright.
    """
    old_connect_info = get_data_local_file(settingsfile)

    from ConfigParser import SafeConfigParser
    config = SafeConfigParser()
    config.read(settingsfile)

    if connect_info['reconnection'] != old_connect_info['reconnection']:
        config.set('Connection', 'reconnection',
                   str(connect_info['reconnection']))
        with open('.settings', 'wb') as configfile:
            config.write(configfile)

    if connect_info['parameters'] != old_connect_info['parameters']:
        config.set('Connection', 'parameters',
                   str(connect_info['parameters']))
        with open('.settings', 'wb') as configfile:
            config.write(configfile)

    return True
