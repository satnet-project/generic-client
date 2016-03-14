# coding=utf-8
import misc
import ConfigParser
import logging

from PySide import QtGui, QtCore
from errors import SettingsCorrupted

"""
   Copyright 2015, 2016 Samuel Góngora García
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

# TODO Gets a "Segmentation fault (core dumped)" after opens this window.

class ConfigurationWindow(QtGui.QDialog):
    def __init__(self, settings=None):
        super(ConfigurationWindow, self).__init__()
        self.settings_file = settings
        self.setWindowTitle("SatNet client - Advanced configuration")

        self.serverInterface()
        self.serialInterface()
        self.UDPInterface()
        self.TCPInterface()
        self.controlInterface()

        import platform
        os = platform.linux_distribution()
        if os[0] == 'debian':
            self.setMinimumSize(800, 330)
        else:
            self.setMinimumSize(800, 300)

        # Read fields
        try:
            self.CONNECTION_INFO = misc.get_data_local_file('.settings')
        except:
            logging.error("Some fields are lost or corrupted")
            raise SettingsCorrupted("Some fields are lost or corrupted")

        self.setfields()

        self.FieldLabelTCPIPSend.setEnabled(False)
        self.FieldLabelTCPPortSend.setEnabled(False)
        self.FieldLabelTCPIPReceive.setEnabled(False)
        self.FieldLabelTCPPortRececeive.setEnabled(False)

    def setfields(self):
        self.FieldLabelServer.setText(self.CONNECTION_INFO['serverip'])
        self.FieldLabelPort.setText(str(self.CONNECTION_INFO['serverport']))
        self.FieldLabelUDPIpSend.setText(self.CONNECTION_INFO['udpipsend'])
        self.FieldLabelUDPPortSend.setText(self.CONNECTION_INFO['udpportsend'])
        self.FieldLabelUDPIPReceive.setText(self.CONNECTION_INFO['udpipreceive'])
        self.FieldLabelUDPPortRececeive.setText(str(self.CONNECTION_INFO['udpportreceive']))
        self.FieldLabelTCPIPSend.setText(self.CONNECTION_INFO['tcpipsend'])
        self.FieldLabelTCPPortSend.setText(self.CONNECTION_INFO['tcpportsend'])
        self.FieldLabelTCPIPReceive.setText(self.CONNECTION_INFO['tcpipreceive'])
        self.FieldLabelTCPPortRececeive.setText(str(self.CONNECTION_INFO['tcpportreceive']))
        self.FieldLabelSerialPort.setText(self.CONNECTION_INFO['serialport'])
        self.FieldLabelSerialBaudRate.setText(self.CONNECTION_INFO['baudrate'])

    def serverInterface(self):
        """
        Server interface
        """
        serverParameters = QtGui.QGroupBox(self)
        grid = QtGui.QGridLayout(serverParameters)
        serverParameters.setLayout(grid)

        LabelServer = QtGui.QLabel("Server address:")
        LabelServer.setFixedWidth(150)
        self.FieldLabelServer = QtGui.QLineEdit()
        self.FieldLabelServer.setFixedWidth(200)
        LabelPort = QtGui.QLabel("Server port:")
        LabelPort.setFixedWidth(150)
        self.FieldLabelPort = QtGui.QLineEdit()
        self.FieldLabelPort.setFixedWidth(200)

        grid.addWidget(LabelServer, 0, 0, 1, 1)
        grid.addWidget(self.FieldLabelServer, 0, 1, 1, 1)
        grid.addWidget(LabelPort, 1, 0, 1, 1)
        grid.addWidget(self.FieldLabelPort, 1, 1, 1, 1)

        serverParameters.setTitle("SatNet server")
        serverParameters.move(10, 10)

    def serialInterface(self):
        """
        Serial interface
        """
        serialParameters = QtGui.QGroupBox(self)
        serialGrid = QtGui.QGridLayout(serialParameters)
        serialParameters.setLayout(serialGrid)

        LabelSerialPort = QtGui.QLabel("Serial port              ")
        LabelSerialPort.setFixedWidth(150)
        self.FieldLabelSerialPort = QtGui.QLineEdit()
        self.FieldLabelSerialPort.setFixedWidth(200)
        LabelSerialBaudRate = QtGui.QLabel("Serial baud rate         ")
        LabelSerialPort.setFixedWidth(150)
        self.FieldLabelSerialBaudRate = QtGui.QLineEdit()
        self.FieldLabelSerialBaudRate.setFixedWidth(200)

        serialGrid.addWidget(LabelSerialPort, 0, 0, 1, 1)
        serialGrid.addWidget(self.FieldLabelSerialPort, 0, 1, 1, 1)
        serialGrid.addWidget(LabelSerialBaudRate, 2, 0, 1, 1)
        serialGrid.addWidget(self.FieldLabelSerialBaudRate, 2, 1, 1, 1)

        serialParameters.setTitle("Serial interface")
        serialParameters.move(410, 10)

    def UDPInterface(self):
        """
        UDP interface
        """
        udpParameters = QtGui.QGroupBox(self)
        udpGrid = QtGui.QGridLayout(udpParameters)
        udpParameters.setLayout(udpGrid)

        LabelUDPIPSend = QtGui.QLabel("UDP remote IP:")
        LabelUDPIPSend.setFixedWidth(150)
        self.FieldLabelUDPIpSend = QtGui.QLineEdit()
        self.FieldLabelUDPIpSend.setFixedWidth(200)
        LabelUPDPortSend = QtGui.QLabel("UDP remote port:")
        LabelUPDPortSend.setFixedWidth(150)
        self.FieldLabelUDPPortSend = QtGui.QLineEdit()
        self.FieldLabelUDPPortSend.setFixedWidth(200)
        LabelUDPIPReceive = QtGui.QLabel("UDP local IP:")
        LabelUDPIPReceive.setFixedWidth(150)
        self.FieldLabelUDPIPReceive = QtGui.QLineEdit()
        self.FieldLabelUDPIPReceive.setFixedWidth(200)
        LabelUDPPortReceive = QtGui.QLabel("UDP local port:")
        LabelUDPPortReceive.setFixedWidth(150)
        self.FieldLabelUDPPortRececeive = QtGui.QLineEdit()
        self.FieldLabelUDPPortRececeive.setFixedWidth(200)

        udpGrid.addWidget(LabelUDPIPSend, 0, 0, 1, 1)
        udpGrid.addWidget(self.FieldLabelUDPIpSend, 0, 1, 1, 1)
        udpGrid.addWidget(LabelUPDPortSend, 1, 0, 1, 1)
        udpGrid.addWidget(self.FieldLabelUDPPortSend, 1, 1, 1, 1)
        udpGrid.addWidget(LabelUDPIPReceive, 2, 0, 1, 1)
        udpGrid.addWidget(self.FieldLabelUDPIPReceive, 2, 1, 1, 1)
        udpGrid.addWidget(LabelUDPPortReceive, 3, 0, 1, 1)
        udpGrid.addWidget(self.FieldLabelUDPPortRececeive, 3, 1, 1, 1)

        udpParameters.setTitle("UDP interface")
        udpParameters.move(10, 105)

    def TCPInterface(self):
        """
        TCP interface
        """
        tcpParameters = QtGui.QGroupBox(self)
        tcpGrid = QtGui.QGridLayout(tcpParameters)
        tcpParameters.setLayout(tcpGrid)

        LabelTCPIPSend = QtGui.QLabel("TCP remote IP:")
        LabelTCPIPSend.setFixedWidth(150)
        self.FieldLabelTCPIPSend = QtGui.QLineEdit()
        self.FieldLabelTCPIPSend.setFixedWidth(200)
        LabelTCPPortSend = QtGui.QLabel("TCP remote port:")
        LabelTCPPortSend.setFixedWidth(150)
        self.FieldLabelTCPPortSend = QtGui.QLineEdit()
        self.FieldLabelTCPPortSend.setFixedWidth(200)
        LabelTCPIPReceive = QtGui.QLabel("TCP local IP:")
        LabelTCPIPReceive.setFixedWidth(150)
        self.FieldLabelTCPIPReceive = QtGui.QLineEdit()
        self.FieldLabelTCPIPReceive.setFixedWidth(200)
        LabelTCPPortReceive = QtGui.QLabel("TCP local port:")
        LabelTCPPortReceive.setFixedWidth(150)
        self.FieldLabelTCPPortRececeive = QtGui.QLineEdit()
        self.FieldLabelTCPPortRececeive.setFixedWidth(200)

        tcpGrid.addWidget(LabelTCPIPSend, 0, 0, 1, 1)
        tcpGrid.addWidget(self.FieldLabelTCPIPSend, 0, 1, 1, 1)
        tcpGrid.addWidget(LabelTCPPortSend, 1, 0, 1, 1)
        tcpGrid.addWidget(self.FieldLabelTCPPortSend, 1, 1, 1, 1)
        tcpGrid.addWidget(LabelTCPIPReceive, 2, 0, 1, 1)
        tcpGrid.addWidget(self.FieldLabelTCPIPReceive, 2, 1, 1, 1)
        tcpGrid.addWidget(LabelTCPPortReceive, 3, 0, 1, 1)
        tcpGrid.addWidget(self.FieldLabelTCPPortRececeive, 3, 1, 1, 1)

        tcpParameters.setTitle("TCP interface")
        tcpParameters.move(410, 105)

    def controlInterface(self):
        """
        Control interface
        """
        controlParameters = QtGui.QGroupBox(self)
        controlGrid = QtGui.QGridLayout(controlParameters)
        controlParameters.setLayout(controlGrid)

        self.buttonBox = QtGui.QDialogButtonBox()
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close |
                                     QtGui.QDialogButtonBox.Save)

        self.buttonBox.button(QtGui.QDialogButtonBox.Close).clicked.connect(
            self.closeWindow)
        self.buttonBox.button(QtGui.QDialogButtonBox.Save).clicked.connect(
            self.save)

        controlGrid.addWidget(self.buttonBox, 0, 0, 1, 2)

        import platform
        os = platform.linux_distribution()
        if os[0] == 'debian':
            controlParameters.move(590, 265)
        else:
            controlParameters.move(590, 240)

    def closeWindow(self):
        self.close()

    def save(self):
        config = ConfigParser.SafeConfigParser()
        config.read(".settings")

        self.CONNECTION_INFO = misc.get_data_local_file(
            settingsfile='.settings')

        server = self.FieldLabelServer.text()
        port = self.FieldLabelPort.text()
        udpipsend = self.FieldLabelUDPIpSend.text()
        udpportsend = self.FieldLabelUDPPortSend.text()
        udpipreceive = self.FieldLabelUDPIPReceive.text()
        udpportreceive = self.FieldLabelUDPPortRececeive.text()
        tcpipsend = self.FieldLabelTCPIPSend.text()
        tcpportsend = self.FieldLabelTCPPortSend.text()
        tcpipreceive = self.FieldLabelTCPIPReceive.text()
        tcpportreceive = self.FieldLabelTCPPortRececeive.text()

        if self.CONNECTION_INFO['serverip'] != server:
            config.set('server', 'serverip', str(server))
            with open('.settings', 'wb') as configfile:
                config.write(configfile)
        if self.CONNECTION_INFO['serverport'] != port:
            config.set('server', 'serverport', str(port))
            with open('.settings', 'wb') as configfile:
                config.write(configfile)
        if self.CONNECTION_INFO['udpipsend'] != udpipsend:
            config.set('udp', 'udpipsend', str(udpipsend))
            with open('.settings', 'wb') as configfile:
                config.write(configfile)
        if self.CONNECTION_INFO['udpportsend'] != udpportsend:
            config.set('udp', 'udpportsend', str(udpportsend))
            with open('.settings', 'wb') as configfile:
                config.write(configfile)
        if self.CONNECTION_INFO['udpipreceive'] != udpipreceive:
            config.set('udp', 'udpipreceive', str(udpipreceive))
            with open('.settings', 'wb') as configfile:
                config.write(configfile)
        if self.CONNECTION_INFO['udpportreceive'] != udpportreceive:
            config.set('udp', 'udpportreceive', str(udpportreceive))
            with open('.settings', 'wb') as configfile:
                config.write(configfile)
        if self.CONNECTION_INFO['tcpipsend'] != tcpipsend:
            config.set('tcp', 'tcpipsend', str(tcpipsend))
            with open('.settings', 'wb') as configfile:
                config.write(configfile)
        if self.CONNECTION_INFO['tcpportsend'] != tcpportsend:
            config.set('tcp', 'tcpportsend', str(tcpportsend))
            with open('.settings', 'wb') as configfile:
                config.write(configfile)
        if self.CONNECTION_INFO['tcpipreceive'] != tcpipreceive:
            config.set('tcp', 'tcpipreceive', str(tcpipreceive))
            with open('.settings', 'wb') as configfile:
                config.write(configfile)
        if self.CONNECTION_INFO['tcpportreceive'] != tcpportreceive:
            config.set('tcp', 'tcpportreceive', str(tcpportreceive))
            with open('.settings', 'wb') as configfile:
                config.write(configfile)

        self.close()
