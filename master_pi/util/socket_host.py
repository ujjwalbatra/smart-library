"""
provides socket utility for listening for login
"""

import json
import socket


class SocketHost(object):
    """
    provides socket utility for listening for login
    """
    CONFIG_FILE = 'master_pi/config.json'

    def __init__(self):
        self.__get_host_and_port()
        self.__socket_connection = None
        self.__start_listening()

    def wait_for_message(self):
        """
        Waits for a client to connect and send data

        Returns:
            string: string sent by the client
        """

        self.__wait_for_connection()
        message = self.__socket_connection.recv(4096).decode()

        return message

    def send_message(self, message):
        """
        Sends a string to the client

        Args:
            message: string to send to the client
        """

        self.__socket_connection.sendall(message.encode())

    def close(self):
        """
        Releases the socket and stops the server listening for connections
        """

        self.__socket_connection.close()
        self.__socket_connection = None

    def __start_listening(self):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        address = (self.__host, self.__port)
        self.__socket.bind(address)
        self.__socket.listen()

    def __get_host_and_port(self):
        with open(self.CONFIG_FILE) as config_file:
            config_json = json.load(config_file)
            self.__host = config_json["sockets"]['host_ip']
            self.__port = int(config_json["sockets"]['host_port'])

    def __wait_for_connection(self):
        self.__socket_connection, _ = self.__socket.accept()
