# coding=utf-8
"""
   Copyright 2015 Samuel Góngora García

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

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from PyQt4 import QtGui
from PyQt4 import QtCore
import sys
import getopt
import os

from Queue import Queue

from twisted.python import log

import logging

from gs_interface import GroundStationInterface


class Client():
    """
    This class starts the client using the data provided by user interface.

    :ivar CONNECTION_INFO:
        This variable contains the following data: username, password, slot_id, 
        connection (either 'serial' or 'udp'), serialport, baudrate, ip, port.
    :type CONNECTION_INFO:
        L{Dictionary}

    :ivar

    """
    def __init__(self, CONNECTION_INFO):
        self.CONNECTION_INFO = CONNECTION_INFO

    def createConnection(self):
        """
        New interface
        """
        gsi = GroundStationInterface(self.CONNECTION_INFO, "Vigo")

        global connector

        connector = reactor.connectSSL('localhost', 1234,\
         ClientReconnectFactory(self.CONNECTION_INFO, gsi),\
          ClientContextFactory())

        return connector


"""
QDialog, QWidget or QMainWindow, which is better in this situation?
"""
class SATNetGUI(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)

        self.initUI()

    def _test(self):
        log.msg("tested!")

    def run(self):
        self.runKISSThread()
        # self.runClientThread()

    """
    Run threads associated to KISS protocol
    """
    def runKISSThread(self):
        # QObject.connect(self.workerKISSThread, SIGNAL( "readingPort( PyQt_PyObject )" ), self._test)
        # QObject.connect( self.workerKISSThread, SIGNAL( "primaryValue( PyQt_PyObject )" ), self.primaryValueFromThread )
        # QObject.connect( self.workerKISSThread, SIGNAL( "primaryRange( PyQt_PyObject )" ), self.primaryRangeFromThread )
        # QObject.connect( self.workerKISSThread, SIGNAL( "primaryText( PyQt_PyObject )" ), self.primaryTextFromThread )
        # QObject.connect( self.workerKISSThread, SIGNAL( "secondaryValue( PyQt_PyObject )" ), self.secondaryValueFromThread )
        # QObject.connect( self.workerKISSThread, SIGNAL( "secondaryRange( PyQt_PyObject )" ), self.secondaryRangeFromThread )
        # QObject.connect( self.workerKISSThread, SIGNAL( "secondaryText( PyQt_PyObject )" ), self.secondaryTextFromThread )
        
        # KISSTNC thread
        self.workerKISSThread.start()

    """
    Run threads associated to information output
    """
    def runStdoutThread(self):
        self.workerStdoutThread.start()

    # """
    # Run threads associated to UI interface
    # """
    # def runClientThread(self):
    #     self.workerClientThread.start()

    def NewConnection(self):
        """
        Create a new connection by loading the connection parameters from 
        the command line or from the interface window.
        """
        self.CONNECTION_INFO = {}

        try:
            # was opts, args
            opts= getopt.getopt(sys.argv[1:],"hfgu:p:t:c:s:b:i:u:",\
             ["username=", "password=", "slot=", "connection=", "serialport=",\
              "baudrate=", "ip=", "udpport="])
        except getopt.GetoptError:
            print "error"

        if ('-g','') in opts:
            for opt, arg in opts:
                if opt in ("-u", "--username"):
                    self.CONNECTION_INFO['username']  = arg
                elif opt in ("-p", "--password"):
                    self.CONNECTION_INFO['password']  = arg
                elif opt in ("-t", "--slot"):
                    self.CONNECTION_INFO['slot_id']  = arg
                elif opt in ("-c", "--connection"):
                    self.CONNECTION_INFO['connection'] = arg
                elif opt in ("-s", "--serialport"):
                    self.CONNECTION_INFO['serialport']  = arg
                elif opt in ("-b", "--baudrate"):
                    self.CONNECTION_INFO['baudrate']  = arg
                elif opt in ("-i", "--ip"):
                    self.CONNECTION_INFO['ip']  = arg
                elif opt in ("-u", "--udpport"):
                    self.CONNECTION_INFO['udpport']  = int(arg)
            self.paramValidation()

        else:
            self.CONNECTION_INFO['username'] = str(self.LabelUsername.text())
            self.CONNECTION_INFO['password'] = str(self.LabelPassword.text())
            self.CONNECTION_INFO['slot_id'] = int(self.LabelSlotID.text())
            self.CONNECTION_INFO['connection'] =\
             str(self.LabelConnection.currentText())
            self.CONNECTION_INFO['serialport'] =\
             str(self.LabelSerialPort.currentText())
            self.CONNECTION_INFO['baudrate'] = str(self.LabelBaudrate.text())
            self.CONNECTION_INFO['ip'] = self.LabelUDP.text()
            print self.LabelUDPPort.text()
            # self.CONNECTION_INFO['udpport'] = int(self.LabelUDPPort.text())

        self.c = Client(self.CONNECTION_INFO).createConnection()

    # """
    # Stops all the thread associated to the KISS protocol
    # """
    # def cancelThread( self ):
    #     self.workerKISSThread.stop()

    # def jobFinishedFromThread( self, success ):
    #     self.workerKISSThread.stop()
    #     self.primaryBar.setValue(self.primaryBar.maximum())
    #     self.secondaryBar.setValue(self.secondaryBar.maximum())
    #     self.emit( SIGNAL( "jobFinished( PyQt_PyObject )" ), success )
    #     self.closeButton.setEnabled( True )

    # def primaryValueFromThread( self, value ):
    #     self.primaryBar.setValue(value)

    # def primaryRangeFromThread( self, range_vals ):
    #     self.primaryBar.setRange( range_vals[ 0 ], range_vals[ 1 ] )

    # def primaryTextFromThread( self, value ):
    #     self.primaryLabel.setText(value)

    # def secondaryValueFromThread( self, value ):
    #     self.secondaryBar.setValue(value)

    # def secondaryRangeFromThread( self, range_vals ):
    #     self.secondaryBar.setRange( range_vals[ 0 ], range_vals[ 1 ] )

    # def secondaryTextFromThread( self, value ):
    #     self.secondaryLabel.setText(value)

    def initUI(self):

        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))
        self.setFixedSize(1300, 800)
        self.setWindowTitle("SATNet client - Generic") 

        # Control buttons.
        buttons = QtGui.QGroupBox(self)
        grid = QtGui.QGridLayout(buttons)
        buttons.setLayout(grid)

        # New connection.
        ButtonNew = QtGui.QPushButton("Connect")
        ButtonNew.setToolTip("Start a new connection")
        ButtonNew.setFixedWidth(145)
        # ButtonNew.setCheckable(True)
        ButtonNew.clicked.connect(self.NewConnection)
        # Close connection.
        ButtonCancel = QtGui.QPushButton("Disconnect")
        ButtonCancel.setToolTip("End current connection")
        ButtonCancel.setFixedWidth(145)
        """
        ButtonCancel.clicked.connect(self.CloseConnection)
        """
        # Load parameters from file
        ButtonLoad = QtGui.QPushButton("Load parameters from file")
        ButtonLoad.setToolTip("Load parameters from <i>config.ini</i> file")
        ButtonLoad.setFixedWidth(298)
        """
        ButtonLoad.clicked.connect(self.LoadParameters)
        """
        # Configuration
        ButtonConfiguration = QtGui.QPushButton("Configuration")
        ButtonConfiguration.setToolTip("Set configuration")
        ButtonConfiguration.setFixedWidth(145)
        """
        ButtonConfiguration.clicked.connect(self.SetConfiguration)
        """
        # Help.
        ButtonHelp = QtGui.QPushButton("Help")
        ButtonHelp.setToolTip("Click for help")
        ButtonHelp.setFixedWidth(145)
        """
        ButtonHelp.clicked.connect(self.usage)
        """
        grid.addWidget(ButtonNew, 0, 0, 1, 1)
        grid.addWidget(ButtonCancel, 0, 1, 1, 1)
        grid.addWidget(ButtonLoad, 1, 0, 1, 2)
        grid.addWidget(ButtonConfiguration, 2, 0, 1, 1)
        grid.addWidget(ButtonHelp, 2, 1, 1, 1)
        buttons.setTitle("Connection")
        buttons.move(10, 10)

        # Parameters group.
        parameters = QtGui.QGroupBox(self)
        layout = QtGui.QFormLayout()
        parameters.setLayout(layout)

        self.LabelUsername = QtGui.QLineEdit()
        self.LabelUsername.setFixedWidth(190)
        layout.addRow(QtGui.QLabel("Username:       "), self.LabelUsername)
        self.LabelPassword = QtGui.QLineEdit()
        self.LabelPassword.setFixedWidth(190)
        self.LabelPassword.setEchoMode(QtGui.QLineEdit.Password)
        layout.addRow(QtGui.QLabel("Password:       "), self.LabelPassword)
        self.LabelSlotID = QtGui.QSpinBox()
        layout.addRow(QtGui.QLabel("slot_id:        "), self.LabelSlotID)

        self.LabelConnection = QtGui.QComboBox()
        self.LabelConnection.addItems(['serial', 'udp'])
        """
        self.LabelConnection.activated.connect(self.CheckConnection)
        """
        layout.addRow(QtGui.QLabel("Connection:     "), self.LabelConnection)
        self.LabelSerialPort = QtGui.QComboBox()
        from glob import glob
        ports = glob('/dev/tty[A-Za-z]*')
        self.LabelSerialPort.addItems(ports)
        layout.addRow(QtGui.QLabel("Serial port:    "), self.LabelSerialPort)
        self.LabelBaudrate = QtGui.QLineEdit()
        layout.addRow(QtGui.QLabel("Baudrate:       "), self.LabelBaudrate)
        self.LabelUDP = QtGui.QLineEdit()
        layout.addRow(QtGui.QLabel("UDP:            "), self.LabelUDP)
        self.LabelUDPPort = QtGui.QLineEdit()
        layout.addRow(QtGui.QLabel("UDP port:       "), self.LabelUDPPort)

        parameters.setTitle("User data")
        parameters.move(10, 145)

        # Configuration group.
        configuration = QtGui.QGroupBox(self)
        configurationLayout = QtGui.QVBoxLayout()
        configuration.setLayout(configurationLayout)

        self.LoadDefaultSettings =\
         QtGui.QCheckBox("Automatically load settings from 'config.ini'")
        configurationLayout.addWidget(self.LoadDefaultSettings)
        self.AutomaticReconnection =\
         QtGui.QCheckBox("Reconnect after a failure")
        configurationLayout.addWidget(self.AutomaticReconnection)

        configuration.setTitle("Basic configuration")
        configuration.move(10, 400)

        # Logo.
        self.LabelLogo = QtGui.QLabel(self)
        self.LabelLogo.move(20, 490)
        pic = QtGui.QPixmap(os.getcwd() + "/logo.png")
        self.LabelLogo.setPixmap(pic)
        self.LabelLogo.show()

        # Console
        self.console = QtGui.QTextBrowser(self)
        self.console.move(340, 10)
        self.console.resize(950, 780)
        self.console.setFont(QtGui.QFont('SansSerif', 10))

        try:
            opts = getopt.getopt(sys.argv[1:],"hfgu:p:t:c:s:b:i:u:",\
             ["username=", "password=", "slot=", "connection=", "serialport=",\
              "baudrate=", "ip=", "udpport="])
        except getopt.GetoptError:
            print "error"

        if ('-g', '') in opts:
            for opt, arg in opts:
                if opt == "-u":
                    self.LabelUsername.setText(arg)
                elif opt == "-p":
                    self.LabelPassword.setText(arg)
                elif opt == "-t":
                    self.LabelSlotID.setValue(arg)
                elif opt == "-c":
                    index = self.LabelConnection.findText(arg)
                    self.LabelConnection.setCurrentIndex(index)
                elif opt == "-s":
                    index = self.LabelSerialPort.findText(arg)
                    self.LabelSerialPort.setCurrentIndex(index)
                elif opt == "-b":
                    self.LabelBaudrate.setText(arg)
                elif opt == "-i":
                    self.LabelUDP.setText(arg)
                elif opt == "-u":
                    self.LabelUDPPort.setText(arg)

        # reconnection, parameters = self.LoadSettings()
        # if reconnection == 'yes':
        #     self.AutomaticReconnection.setChecked(True)
        # elif reconnection == 'no':
        #     self.AutomaticReconnection.setChecked(False)
        # if parameters == 'yes':
        #     self.LoadDefaultSettings.setChecked(True)
        #     self.LoadParameters()
        # elif parameters == 'no':
        #     self.LoadDefaultSettings.setChecked(False)

    """
    Functions designed to output information
    """
    @pyqtSlot(str)
    def append_text(self,text):
        self.console.moveCursor(QTextCursor.End)
        self.console.insertPlainText(text)

    def closeEvent(self, event):       
        reply = QtGui.QMessageBox.question(self, 'Exit confirmation',
            "Are you sure to quit?", QtGui.QMessageBox.Yes | 
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            try:
                #self.c.disconnect()
                self.workerKISSThread.stop()
                reactor.stop()
            except Exception:
                log.msg("Reactor not running.")

            event.accept()
        else:
            event.ignore()  


"""
Class associated to KISS protocol
"""
class KISSThread(QThread):
    
    def __init__(self, parent = None):
        QThread.__init__(self, parent)

        """
        Opening port
        """
        import kiss
        try:
            log.msg('Opening serial port')
            self.kissTNC = kiss.KISS('/dev/ttyS1', '9000')
        except Exception as e:
            log.err('Error opening port')
            log.err(e)

        try:
            self.kissTNC.start()
        except Exception as e:
            log.err('Error starting KISS protocol')
            log.err(e)

    def run(self):
        log.msg('Listening')
        self.running = True
        success = self.doWork(self.kissTNC)
        # self.emit(SIGNAL("readingPort( PyQt_PyObject )"), success )
    
    def stop(self):
        log.msg('Stopping serial port')
        self.running = False
        pass
    
    def doWork(self):
        return True
    
    def cleanUp(self):
        pass


class OperativeKISSThread(KISSThread):
    def __init__(self, parent = None):
        KISSThread.__init__(self, parent)
    
    def doWork(self, kissTNC):
        kissTNC.read(callback=self.catchValue)
        return True

    def catchValue(self, frame):
        print "hola"
        print frame
        log.msg(frame)


# """
# Class associated to output information
# """
# class StdoutThread(QThread):
#     def __init__(self, parent = None):
#         QThread.__init__(self, parent)

#     def run(self):
#         log.msg('Streaming text to text widget')
#         self.running = True
#         success = self.doWork()

#     def stop(self):
#         self.running = False
#         pass

#     def doWork(self):
#         return True

#     def cleanup(self):
#         pass


# class OperativeStdoutThread(StdoutThread):
#     def __init__(self, parent = None):
#         StdoutThread.__init__(self, parent)

#     def doWork(self):
#         """
#         Insert work actions
#         """
#         my_receiver = MyReceiver(queue)
#         my_receiver.mysignal.connect
#         return True 


"""
Objects designed for output the information
"""
class WriteStream(object):
    def __init__(self,queue):
        print "abierto WriteStream"
        self.queue = queue

    def write(self, text):
        self.queue.put(text)

    def flush(self):
        pass


"""
A QObject (to be run in a QThread) which sits waiting for data to come 
through a Queue.Queue().
It blocks until data is available, and one it has got something from the 
queue, it sends it to the "MainThread" by emitting a Qt Signal 
"""
class MyReceiver(QThread):
    mysignal = pyqtSignal(str)

    def __init__(self,queue,*args,**kwargs):
        QThread.__init__(self,*args,**kwargs)
        self.queue = queue

    @pyqtSlot()
    def run(self):
        while True:
            text = self.queue.get()
            self.mysignal.emit(text)


if __name__ == '__main__':

    # Create Queue and redirect sys.stdout to this queue
    queue = Queue()
    sys.stdout = WriteStream(queue)

    log.startLogging(sys.stdout)

    # log.PythonLoggingObserver()
    # logging.basicConfig(stream=WriteStream(queue), level=logging.DEBUG)

    qapp = QApplication(sys.argv)
    app = SATNetGUI()
    """
    Threads
    """
    app.workerKISSThread = OperativeKISSThread()
    # app.workerStdoutThread = OperativeStdoutThread()
    # d.workerClientThread = OperativeClientThread()
    app.setWindowIcon(QIcon('logo.png'))

    app.show()
    app.run()

    # Create thread that will listen on the other end of the queue, and 
    # send the text to the textedit in our application
    my_receiver = MyReceiver(queue)
    my_receiver.mysignal.connect(app.append_text)
    my_receiver.start()

    qapp.exec_()

    # from qtreactor import pyqt4reactor
    # pyqt4reactor.install()

    # from twisted.internet import reactor
    # reactor.run()

    # TO-DO system freezes.
    # sys.exit(app.exec_())
