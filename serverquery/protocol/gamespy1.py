# coding: utf-8
from __future__ import unicode_literals
import re
from collections import OrderedDict

from .. import Server as BaseServer
from ..exceptions import ResponseIncomplete, ResponseMalformed


class Server(BaseServer):
    packets = {
        'status': b'\\status\\',
    }
    parsers = (
        'parse_packets',
        'format_packets',
    )
    formatters = (
        'format_response',
    )

    def parse_packets(self, packets):
        """
        Parse and sort packets received in a response.

        :param packets: List of received packets
        :type packets: list
        :return: List of packets sorted in the original order
        :type return: list

        :raises ResponseIncomplete: if not enough packets
        """
        packets, count = self._sort_packets(packets)
        # check the packet length
        if not count or count > len(packets):
            raise ResponseIncomplete(
                'expected length of {} does not match the actual length {}'.format(count, len(packets))
            )
        return packets

    def format_packets(self, packets):
        """
        Attempt to sort packets in the original order and parse their contents.

        :param packets: List of packets' contents
        :type packets: list
        :return: List of params
        :type return: list
        """
        return self._parse_params(u''.join(packets))

    def format_response(self, response):
        """
        Turn a formatted response data into an ordered dict.

        :param response: Formatted response
        :type response: tuple
        :return: Response dict
        :type return: collections.OrderedDict
        """
        return OrderedDict(response)

    def _sort_packets(self, packets):
        count = None
        is_final = False
        numbered = {}
        for data in packets:
            data = self._decode(data)
            id = None
            for param, value in self._parse_params(data):
                if id is None and param in ('statusresponse', 'queryid'):
                    # \statusresponse\1 or \queryid\1
                    try:
                        # attempt to read the next piece of data
                        id = int(value)
                    except IndexError:
                        raise ResponseMalformed('invalid queryid')
                    # \queryid\gs1
                    except ValueError:
                        id = 1
                    else:
                        # statusresponse is zero based
                        id += (param == 'statusresponse')
                # this is the final packet
                elif param == 'final':
                    is_final = True
            if is_final:
                count = id
            if id is None:
                raise ResponseMalformed('failed to read packet id')
            numbered[id] = self._fix_packet_contents(data)
        # sort packets by their ids
        return [value for key, value in sorted(numbered.items())], count

    def _parse_params(self, data):
        """
        Split a response into a list of params.

        :param data: Response contents
        :type data: unicode
        :return: List of (key, value) param tuples
        :type return: list
        """
        params = []
        split = data.split('\\')
        for i, key in enumerate(split):
            # skip values
            if not i % 2:
                continue
            # fetch the value
            try:
                value = split[i + 1]
            except IndexError:
                pass
            else:
                params.append((key, value))
        return params

    def _fix_packet_contents(self, data):
        """
        Remove standard non compliant headers from packet contents.

        :param data: Packet contents
        :type data: unicode
        :return: Packet contents
        :type return: unicode
        """
        return re.sub(r'(?:^\\statusresponse\\\d+|\\eof\\$)', '', data)

    def _decode(self, data):
        """
        Decode a piece of data into a unicode string.

        :param data: Data
        :return: Unicode string
        """
        try:
            return data.decode('utf-8', errors='ignore')
        except (AttributeError, UnicodeDecodeError):
            return self._decode(str(data))
