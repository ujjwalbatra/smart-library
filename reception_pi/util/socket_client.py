import json
import socket


class SocketClient():
    CONFIG_FILE = 'reception_pi/config.json'

    def __init__(self):
        self.__get_host_and_port()
        self.__socket_connection = None

    def send_message(self, message):

        """
        Sends a string to the host then closes the connection

        Args:
            message: string to send to host

        Returns:
            string: 'SUCCESS' or 'FAILURE' depending on whether message was sent successfully
        """

        try:
            self.__connect_to_host()
            self.__send_string(message)
            self.close()
            return "SUCCESS"

        except socket.error:
            return "FAILURE"

    def send_message_and_wait(self, message):

        """
        Sends a string to the host then waits for a response

        Args:
            message: string to send to host

        Returns:
            string: response from host, or 'FAILURE' if connection failed
        """

        try:
            self.__connect_to_host()
            self.__send_string(message)
            response = self.__wait_for_response()
            self.close()

            return response

        except socket.error:
            return "FAILURE"

    def close(self):

        """
        Releases the socket
        """

        self.__socket_connection.close()
        self.__socket_connection = None

    def __get_host_and_port(self):
        with open(self.CONFIG_FILE) as config_file:
            config_json = json.load(config_file)
            self.__host = config_json["sockets"]['master_ip']
            self.__port = int(config_json["sockets"]['master_port'])

    def __connect_to_host(self):
        if not self.__socket_connection:
            address = (self.__host, self.__port)
            self.__socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__socket_connection.connect(address)

    def __send_string(self, string):
        self.__socket_connection.sendall(string.encode())

    def __wait_for_response(self):
        response = self.__socket_connection.recv(4096).decode()
        return response
