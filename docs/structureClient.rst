=========================================
CLient file structure
=========================================

Client classes are as follows. Each class is detailed with its corresponding methods.

+---------------+--------------------------+------------------------+
| Module        | Class                    | Methods                |
+===============+==========================+========================+
| client_amp.py | ClientProtocol           | __init__               |
+---------------+--------------------------+------------------------+
|               |                          | connectionMade         |
+---------------+--------------------------+------------------------+
|               |                          | connectionLost         |
+---------------+--------------------------+------------------------+
|               |                          | user_login             | 
+---------------+--------------------------+------------------------+
|               |                          | vNotifyMsg             |
+---------------+--------------------------+------------------------+
|               |                          | _processframe          |
+---------------+--------------------------+------------------------+
|               |                          | processframe           |
+---------------+--------------------------+------------------------+
|               |                          | vNotifyEvent           |
+---------------+--------------------------+------------------------+

The ClientProtocol class is responsible for creating the connection protocol client.

.. py:function:: __init__(self, CONNECTION_INFO, gsi)
    
    ClientProtocol class initialization through the CONNECTION_INFO variable and the gsi object.

.. py:function:: connectionMade(self)
    
    Method belonging to the protocol responsible for starting the user's connection.

.. py:function:: connectionLost(self)
    
    When the connection is lost this method is executed.

.. py:function:: user_login(self)
    
    This method is responsible for making the AMP calls that initiate the connection.

.. py:function:: vNotifyMsg(self, sMsg)

    AMP call responsible for notifying the user of reception of a message.

.. py:function:: _processframe(self, frame)

    Method associated to frame processing.

.. py:function:: processFrame(self, frame)

    Responsible method of get the frames through the serial port, or through an UPD/TCP connection, and send them using an AMP call.

.. py:function:: vNotifyEvent(self, iEvent, sDetails)

    AMP call responsible for notifying the user of any event related to the remote client or the connection slots.

+---------------+--------------------------+------------------------+
| Module        | Class                    | Methods                |
+===============+==========================+========================+
| client_amp.py | ClientReconnectedFactory | __init__               |
+---------------+--------------------------+------------------------+
|               |                          | startedConnecting      |
+---------------+--------------------------+------------------------+
|               |                          | buildProtocol          |
+---------------+--------------------------+------------------------+
|               |                          | clientConnectionLost   |
+---------------+--------------------------+------------------------+
|               |                          | clientConnectionFailed |
+---------------+--------------------------+------------------------+

The ClientReconnectedFactory class is responsible for managing user logon when this is lost for any reason.

.. py:function:: __init__(


.. py:function:: startedConnecting(self, connector)

    Method called when a connection has been started.

.. py:function:: buildProtocol(self, addr)

    Create an instance of a subclass of Protocol.

.. py:function:: clientConnectionLost(self, connector, reason)

    Called when a established connection is lost.

.. py:function:: clientConnectionFailed(self, connector, reason)

    Called when a connection has failed to connect.

+---------------+--------------------------+------------------------+
| Module        | Class                    | Methods                |
+===============+==========================+========================+
| client_amp.py | CtxFactory               | getContext             |
+---------------+--------------------------+------------------------+

The CtxFactory class handles the defining method to be used in SSL connection.

.. py:function:: getContext(self)

    Setting the connection method.

+---------------+--------------------------+------------------------+
| Module        | Class                    | Methods                |
+===============+==========================+========================+
| client_amp.py | Client                   | __init__               |
+---------------+--------------------------+------------------------+  
|               |                          | createConnection       |
+---------------+--------------------------+------------------------+

The "Client" class starts the connection using Twisted. For this purpose uses the ClientReconnectedFactory class and the ClientProtocol class.

.. py:function:: __init__(


.. py:function:: createConnection(self)

    Create a new interface.

+---------------+--------------------------+------------------------+
| Module        | Class                    | Methods                |
+===============+==========================+========================+
| client_amp.py | SATNetGUI                | __init__               |
+---------------+--------------------------+------------------------+
|               |                          | runKISSThread          |
+---------------+--------------------------+------------------------+
|               |                          | runUDPThread           |
+---------------+--------------------------+------------------------+
|               |                          | runTCPThread           |
+---------------+--------------------------+------------------------+
|               |                          | stopKISSThread         |
+---------------+--------------------------+------------------------+
|               |                          | stopUDPThread          |
+---------------+--------------------------+------------------------+
|               |                          | stopTCPThread          |
+---------------+--------------------------+------------------------+
|               |                          | sendData               |
+---------------+--------------------------+------------------------+
|               |                          | NewConnection          |
+---------------+--------------------------+------------------------+
|               |                          | initUI                 |
+---------------+--------------------------+------------------------+
|               |                          | initFields             |
+---------------+--------------------------+------------------------+
|               |                          | initLogo               |
+---------------+--------------------------+------------------------+
|               |                          | initData               |
+---------------+--------------------------+------------------------+
|               |                          | initConsole            |
+---------------+--------------------------+------------------------+
|               |                          | CloseConnection        |
+---------------+--------------------------+------------------------+
|               |                          | LoadSettings           |
+---------------+--------------------------+------------------------+
|               |                          | LoadParameters         |
+---------------+--------------------------+------------------------+
|               |                          | SetConfiguration       |
+---------------+--------------------------+------------------------+
|               |                          | CheckConnection        |
+---------------+--------------------------+------------------------+
|               |                          | usage                  |
+---------------+--------------------------+------------------------+
|               |                          | center                 |
+---------------+--------------------------+------------------------+
|               |                          | append_text            |
+---------------+--------------------------+------------------------+
|               |                          | closeEvent             |
+---------------+--------------------------+------------------------+

SATNetGUI class contains the methods necessary for the creation of the main user interface.

.. py:function:: __init__(self, parent = None)

    This initial method starts the user interface and the signals and queues required for QThreads.

.. py:function:: runKISSThread(self)

    Create an object of class OperativeKISSThread and starts the QThread calling the start method.

.. py:function:: runUDPThread(self)

    Create an object of class OperativeUDPThread and starts the QThread calling the start method.

.. py:function:: runTCPThread(self)

    Create an object of class OperativeTCPThread and starts the QThread calling the start method.

.. py:function:: stopKISSThread(self)

    Stops the QThread that handles serial communication calling the stop method. 

.. py:function:: stopUDPThread(self)

    Stops the QThread that handles UDP communication calling the stop method.

.. py:function:: stopTCPThread(self)

    Stops the QThread that handles TCP communication calling the stop method.

.. py:function:: sendData(self, result)

    Invokes the _manageframe method of protocol GroundStationInterface.

.. py:function:: NewConnection(self)

    Create a new connection by loading the connection parameters from the interface window.

.. py:function:: initUI(self)

    UI starts by passing the basic values such as size and name.

.. py:function:: initButtons(self)

    Starts the control buttons panel of user interface.

.. py:function:: initFields(self)

    Starts the data entry field.

.. py:function:: initLogo(self)

    Method which defines the logo of the main window.

.. py:function:: initData(self)

    Reads the program settings from .settings file and edit them accordingly.

.. py:function:: initConsole(self)

    Starts the console where the status messages will be shown.

.. py:function:: CloseConnection(self)

    Ends the current connection without finishing the program.

.. py:function:: LoadSettings(self)

    | Loads configuration settings from .settings file and get back them to user.
    | Duplicated function. Must be merged with initData method.

.. py:function:: LoadParameters(self)

    It loads user parameters, as username and password, from config.ini file.

.. py:function:: SetConfiguration(self)

    Method responsible to create advanced user settings window.

.. py:function:: CheckConnection(self)

    Method which changes the UI according to the connection selected.

.. py:function:: usage(self)

    Method which show on screen a tiny text help.

.. py:function:: center(self)

    Method which centers the main window on screen.

.. py:function:: append_text(self, text)

    Method responsible to add the messages to the user console.

.. py:function:: closeEvent(self, text)

    Method responsible of, when the program is closed, the communication ends.

+---------------+--------------------------+------------------------+
| Module        | Class                    | Methods                |
+===============+==========================+========================+
| client_amp.py | DateDialog               | __init__               |
+---------------+--------------------------+------------------------+
|               |                          | getConfiguration       |
+---------------+--------------------------+------------------------+
|               |                          | buildWindow            |
+---------------+--------------------------+------------------------+

The DateDialog class contains the methods needed to display the user configuration advanced settings.

.. py:function:: __init__(self)

    Method needed to start the window.

.. py:function:: getConfiguration(self)

    Method responsible of reading the settings available on screen.

.. py:function:: buildWindow(self)

    Static method in charge of creating the configuration window through a call from the SATNetGUI class. This method will return the configuration values.

+---------------+--------------------------+------------------------+
| Module        | Class                    | Methods                |
+===============+==========================+========================+
| client_amp.py | WriteStream              | __init__               |
+---------------+--------------------------+------------------------+
|               |                          | write                  |
+---------------+--------------------------+------------------------+
|               |                          | flush                  |
+---------------+--------------------------+------------------------+

The WriteStream class create the queue needs for the console text.

.. py:function:: __init__(self)

    Class initialization. Create the queue required for this class.

.. py:function:: write(self)

    Collect the text and adds it to the queue created.

.. py:function:: flush(self)

    Not docummented.

+---------------+--------------------------+------------------------+
| Module        | Class                    | Methods                |
+===============+==========================+========================+
| client_amp.py | MyReceiver               | __init__               |
+---------------+--------------------------+------------------------+
|               |                          | run                    |
+---------------+--------------------------+------------------------+

An object class inherited from the class QThread. Used to manage the thread that handles text console.

.. py:function:: __init__(self)

    Class initialization.

.. py:function:: run(self)

    Method main thread. Collect the text from the queue and output as a signal.

+---------------+--------------------------+------------------------+
| Module        | Class                    | Methods                |
+===============+==========================+========================+
| client_amp.py | ResultObj                | __init__               |
+---------------+--------------------------+------------------------+

Class responsible for transforming the value received in an object of the QThread module.

.. py:function:: __init__(self)

    Class initialization.

+-----------------+--------------------------+------------------------+
| Module          | Class                    | Methods                |
+=================+==========================+========================+
| gs_interface.py | GroundStationInterface   | __init__               |
+-----------------+--------------------------+------------------------+
|                 |                          | _manageFrame           |
+-----------------+--------------------------+------------------------+
|                 |                          | _updateLocalFile       |
+-----------------+--------------------------+------------------------+
|                 |                          | connectProtocol        | 
+-----------------+--------------------------+------------------------+
|                 |                          | disconnectedProtocol   |
+-----------------+--------------------------+------------------------+

Class responsible for initiating the basic methods of the client connection with the tracking station.

.. py:function:: __init__(self, CONNECTION_INFO, GS, AMP)

    Class initialization. Collect settings of the connection.

.. py:function:: _manageFrame(self, result)

    Checks if the AMP connection is available. If it is not available this method saves the messages in a local file.

.. py:function:: _updateLocalFile(self, frame)

    Method responsible, in the absence of a connection, save the received messages.

.. py:function:: connectedProtocol(self, AMP)

    This method it is call when the protocol gets connected.

.. py:function:: disconnectedProtocol(self)

    This method it is call when the protocol gets disconnected.

+-----------------+--------------------------+------------------------+
| Module          | Class                    | Methods                |
+=================+==========================+========================+
| gs_interface.py | UDPThread                | __init__               |
+-----------------+--------------------------+------------------------+
|                 |                          | run                    |
+-----------------+--------------------------+------------------------+
|                 |                          | stop                   |
+-----------------+--------------------------+------------------------+
|                 |                          | doWork                 | 
+-----------------+--------------------------+------------------------+
|                 |                          | cleanUp                |
+-----------------+--------------------------+------------------------+

An object class inherited from the class QThread. Used to manage the thread that handles the UDP protocol.

.. py:function:: __init__(self, parent = None)

    It opens the UPD socket.

.. py:function:: run(self)

    It starts the QThread execution.

.. py:function:: stop(self)

    This method stops the thread execution.

.. py:function:: doWork(self)

    Not docummented.

.. py:function:: cleanUp(self)

    Not docummented.

+-----------------+--------------------------+------------------------+
| Module          | Class                    | Methods                |
+=================+==========================+========================+
| gs_interface.py | TCPThread                | __init__               |
+-----------------+--------------------------+------------------------+
|                 |                          | run                    |
+-----------------+--------------------------+------------------------+
|                 |                          | stop                   |
+-----------------+--------------------------+------------------------+
|                 |                          | doWork                 | 
+-----------------+--------------------------+------------------------+
|                 |                          | cleanUp                |
+-----------------+--------------------------+------------------------+

An object class inherited from the class QThread. Used to manage the thread that handles the TCP protocol.

.. py:function:: __init__(self, parent = None)

    It opens the TCP socket.

.. py:function:: run(self)

    It starts the QThread execution.

.. py:function:: stop(self)

    This method stops the thread execution.

.. py:function:: doWork(self)

    Not docummented.

.. py:function:: cleanUp(self)

    Not docummented.

+-----------------+--------------------------+------------------------+
| Module          | Class                    | Methods                |
+=================+==========================+========================+
| gs_interface.py | KISSThread               | __init__               |
+-----------------+--------------------------+------------------------+
|                 |                          | run                    |
+-----------------+--------------------------+------------------------+
|                 |                          | stop                   |
+-----------------+--------------------------+------------------------+
|                 |                          | doWork                 | 
+-----------------+--------------------------+------------------------+
|                 |                          | cleanUp                |
+-----------------+--------------------------+------------------------+

An object class inherited from the class QThread. Used to manage the thread that handles the KISS protocol.

.. py:function:: __init__(self, parent = None)

    It creates the KISS protocol.

.. py:function:: run(self)

    It starts the QThread execution.

.. py:function:: stop(self)

    This method stops the thread execution.

.. py:function:: doWork(self)

    Not docummented.

.. py:function:: cleanUp(self)

    Not docummented.

+-----------------+--------------------------+------------------------+
| Module          | Class                    | Methods                |
+=================+==========================+========================+
| gs_interface.py | OperativeUDPThread       | __init__               |
+-----------------+--------------------------+------------------------+
|                 |                          | doWork                 |
+-----------------+--------------------------+------------------------+
|                 |                          | catchValue             |
+-----------------+--------------------------+------------------------+

An object class inherited from the class OperativeUDPThread. Used to manage the UDP reception.

.. py:function:: __init__(self, queue, callback, UDPSignal, parent = None)

    Connects the thread to the callback function.

.. py:function:: doWork(self, UDPSocket)

    It collects the frames from the UDP connection.

.. py:function:: catchValue(self, frame, address)

    Method that collects the received frame and returns it as a signal.

+-----------------+--------------------------+------------------------+
| Module          | Class                    | Methods                |
+=================+==========================+========================+
| gs_interface.py | OperativeTCPThread       | __init__               |
+-----------------+--------------------------+------------------------+
|                 |                          | doWork                 |
+-----------------+--------------------------+------------------------+
|                 |                          | catchValue             |
+-----------------+--------------------------+------------------------+

An object class inherited from the class OperativeTCPThread. Used to manage the TCP reception.

.. py:function:: __init__(self, queue, callback, TCPSignal, parent = None)

    Connects the thread to the callback function.

.. py:function:: doWork(self, TCPSocket)

    It collects the frames from the TCP connection.

.. py:function:: catchValue(self, frame, address)

    Method that collects the received frame and returns it as a signal.

+-----------------+--------------------------+------------------------+
| Module          | Class                    | Methods                |
+=================+==========================+========================+
| gs_interface.py | OperativeKISSThread      | __init__               |
+-----------------+--------------------------+------------------------+
|                 |                          | doWork                 |
+-----------------+--------------------------+------------------------+
|                 |                          | catchValue             |
+-----------------+--------------------------+------------------------+

An object class inherited from the class OperativeKISSThread. Used to manage the KISS reception.

.. py:function:: __init__(self, queue, callback, serialSignal, parent = None)

    Connects the thread to the callback function.

.. py:function:: doWork(self, kissTNC)

    It collects the frames from the serial connection through the KISS protocol.

.. py:function:: catchValue(self, frame)

    Method that collects the received frame and returns it as a signal.



