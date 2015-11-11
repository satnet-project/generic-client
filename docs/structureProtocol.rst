=========================================
Protocol file structure
=========================================

Customer classes are as follows. Each class is detailed with its corresponding methods.

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