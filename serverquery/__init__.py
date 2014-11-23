# coding: utf-8
import socket

from .exceptions import ResponseIncomplete, ResponseMalformed


class Server(object):
    timeout = 1.0

    packets = {}
    parsers = ()
    formatters = ()

    def __init__(self, ip, port, timeout=None):
        self.timeout = timeout or self.timeout
        self.ip = ip
        self.port = port

    def query(self, query):
        result = None
        response = self._query(query)
        if response:
            result = response
            # apply formatters
            for formatter in self.formatters:
                result = getattr(self, formatter)(result)
        return result

    def __getattr__(self, name):
        try:
            packet = self.packets[name]
        except KeyError:
            raise AttributeError
        else:
            return lambda: self.query(packet)

    def _query(self, query):
        response = []
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)
        try:
            sock.connect((self.ip, self.port))
            sock.send(query)
            while True:
                response.append(sock.recv(2048))
                # attempt to parse the response
                try:
                    for parser in self.parsers:
                        response = getattr(self, parser)(response)
                # get more data and try again
                except ResponseIncomplete:
                    pass
                else:
                    # break the while loop
                    break
        except (socket.timeout, ResponseMalformed):
            raise

        return response


class Player(object):
    pass
