import json
import socket


class SocketConnection():
    CONFIG_FILE = 'reception_pi/config.json'

    def __init__(self):
        self.__get_host_and_port()
        self.__socket_connection = None

    def send_message(self, message):
        self.__connect_to_master()
        self.__send_string(message)
        self.close()

    def send_message_and_wait(self, message):
        self.__connect_to_master()
        self.__send_string(message)
        response = self.__wait_for_response()
        self.close()

        return response

    def close(self):
        self.__socket_connection.close()
        self.__socket_connection = None

    def __get_host_and_port(self):
        with open(self.CONFIG_FILE) as config_file:
            config_json = json.load(config_file)
            self.__host = config_json["sockets"]['master_ip']
            self.__port = int(config_json["sockets"]['master_port'])

    def __connect_to_master(self):
        if not self.__socket_connection:
            address = (self.__host, self.__port)
            self.__socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__socket_connection.connect(address)

    def __send_string(self, string):
        self.__socket_connection.sendall(string.encode())

    def __wait_for_response(self):
        response = self.__socket_connection.recv(4096)
        return response
