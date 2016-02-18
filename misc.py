# coding=utf-8
import datetime
import pytz
import sys
import getopt

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
    :param no_microseconds=True: sets whether microseconds should be cleared.
    :return: the just created datetime object with today's date.
    """
    if no_microseconds:
        return pytz.utc.localize(datetime.datetime.utcnow()).replace(
            microsecond=0
        )
    else:
        return pytz.utc.localize(datetime.datetime.utcnow())


def get_now_hour_utc(no_microseconds=True):
    """
    This method returns now's hour in the UTC timezone.
    :param no_microseconds=True: sets whether microseconds should be cleared.
    :return: The time object within the UTC timezone.
    """
    if no_microseconds:
        return datetime.time.utcnow().replace(microsecond=0).time()
    else:
        return datetime.time.utcnow().time()


def get_today_utc():
    """
    This method returns today's date localized with the microseconds set to
    zero.
    :return: the just created datetime object with today's date.
    """
    return pytz.utc.localize(datetime.datetime.utcnow()).replace(
        hour=0, minute=0, second=0, microsecond=0
    )


def get_next_midnight():
    """
    This method returns today's datetime 00am.
    :return: the just created datetime object with today's datetime 00am.
    """
    return pytz.utc.localize(datetime.datetime.today()).replace(
        hour=0, minute=0, second=0, microsecond=0
    ) + datetime.timedelta(days=1)


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


def noArguments():
    argumentsDict = {}
    arguments = ['username', 'password', 'slot', 'connection',
                 'serialport', 'baudrate', 'udpipsend', 'udpportsend',
                 'udpipreceive', 'udpportreceive']
    for i in range(len(arguments)):
        argumentsDict[arguments[i]] = ""

    return argumentsDict


def readArguments(argumentsDict):
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "hfgn:p:t:c:s:b:is:us:ir:ur",
                                   ["name=", "password=",
                                    "slot=", "connection=",
                                    "serialport=",
                                    "baudrate=", "udpipsend=",
                                    "udpportsend=", "udpipreceive=",
                                    "udpportreceive="]
                                   )
    except getopt.GetoptError:
        print "error"

    argumentsDict = {}
    if ('-g', '') in opts:
        for opt, arg in opts:
            if opt == "-n":
                argumentsDict['username'] = arg
            elif opt == "-p":
                argumentsDict['password'] = arg
            elif opt == "-t":
                argumentsDict['slot'] = arg
            elif opt == "-c":
                argumentsDict['connection'] = arg
            elif opt == "-s":
                argumentsDict['serialport'] = arg
            elif opt == "-b":
                argumentsDict['baudrate'] = arg
            elif opt == "-is":
                argumentsDict['udpipsend'] = arg
            elif opt == "-us":
                argumentsDict['udpportsend'] = arg
            elif opt == "-ir":
                argumentsDict['udpipreceive'] = arg
            elif opt == "-ur":
                argumentsDict['udpportreceive'] = arg
    return argumentsDict

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


def get_data_local_file(settingsFile):
    """
    Returns a dictionary which contains the connection's data.
    """

    CONNECTION_INFO = {}

    import ConfigParser
    config = ConfigParser.ConfigParser()
    config.read(settingsFile)

    CONNECTION_INFO['reconnection'] = config.get('Connection',
                                                 'reconnection')
    CONNECTION_INFO['parameters'] = config.get('Connection',
                                               'parameters')
    CONNECTION_INFO['name'] = config.get('Client', 'name')
    CONNECTION_INFO['attempts'] = config.get('Client', 'attempts')
    CONNECTION_INFO['username'] = config.get('User', 'username')
    CONNECTION_INFO['password'] = config.get('User', 'password')
    CONNECTION_INFO['slot_id'] = config.get('User', 'slot_id')
    CONNECTION_INFO['connection'] = config.get('User', 'connection')

    CONNECTION_INFO['serialport'] = config.get('Serial', 'serialport')
    CONNECTION_INFO['baudrate'] = config.get('Serial', 'baudrate')
    CONNECTION_INFO['udpipreceive'] = config.get('udp', 'udpipreceive')
    CONNECTION_INFO['udpportreceive'] = int(config.get('udp',
                                                       'udpportreceive'))
    CONNECTION_INFO['udpipsend'] = config.get('udp', 'udpipsend')
    CONNECTION_INFO['udpportsend'] = config.get('udp', 'udpportsend')
    CONNECTION_INFO['tcpipreceive'] = config.get('tcp', 'tcpipreceive')
    CONNECTION_INFO['tcpportreceive'] = int(config.get('tcp',
                                                       'tcpportreceive'))
    CONNECTION_INFO['tcpipsend'] = config.get('tcp', 'tcpipsend')
    CONNECTION_INFO['tcpportsend'] = config.get('tcp', 'tcpportsend')

    CONNECTION_INFO['serverip'] = config.get('server', 'serverip')
    CONNECTION_INFO['serverport'] = int(config.get('server',
                                                   'serverport'))

    return CONNECTION_INFO
