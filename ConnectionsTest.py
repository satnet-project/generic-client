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


class TestUDPConnection(object):

	def __init__(self, ip, port):
		from socket import socket, AF_INET, SOCK_DGRAM

		ip = str(ip)
		port = int(port)

		sock = socket(AF_INET, SOCK_DGRAM)
		server_address = (ip, port)

		message = "This is the message. It will be repeated"

		self.sendData(sock, message, server_address)

	def sendData(self, sock, message, server_address):
		print "Sending message"
		sock.sendto(message, server_address)

		sock.close()

if __name__ == "__main__":

	ip = '127.0.0.1'
	port = 57008

	main = TestUDPConnection(ip, port)
