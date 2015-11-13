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

El módulo server_amp.py es el encargado de iniciar el servidor de Twisted.

El fichero se puede iniciar en modo debug, en este modo se muestran por pantalla mensajes de aviso cada vez que se crea un deferred o se invoca. También dispone de un modo de ayuda que muestra un pequeño mensaje de ayuda.

La clase SATNETServer, perteneciente al módulo server_amp.py contiene los metodos AMP necesarios.


.. py:function:: dataReceived(self, data)
    
    ClientProtocol class initialization through the CONNECTION_INFO variable and the gsi object.m

.. py:function:: iStartRemote(self, iSLotId)
    
    Method belonging to the protocol responsible for starting the user's connection.

.. py:function:: vEndRemote(self)
    
    Actualmente no está implementado.

.. py:function:: vSendMsg(self, sMsg, iTimestamp)
    
    This method is responsible for making the AMP calls that initiate the connection.