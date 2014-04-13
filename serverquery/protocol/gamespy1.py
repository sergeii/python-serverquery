# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from functools import reduce
from collections import OrderedDict

from serverquery import base


class Server(base.Server):
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
        ordered, count = self._order_packets(packets)
        # check the packet length
        if not count or count > len(ordered):
            raise base.ResponseIncomplete('%s != %s' % (count, len(ordered)))
        return ordered

    def format_packets(self, packets):
        parsed = []
        # sort by packet ids and merge the packets
        merged = []
        for key, value in sorted(packets.items()):
            merged.append(value)
        # split params and construct name => value pairs
        for name, value in self._parse_params(b''.join(merged)):
            parsed.append((name.decode('utf-8', errors='ignore'), value.decode('utf-8', errors='ignore')))
        return parsed

    def format_response(self, response):
        return OrderedDict(response)

    def _order_packets(self, packets):
        count = None
        ordered = {}
        for packet in packets:
            packet_id = None
            for name, value in self._parse_params(packet):
                if not packet_id and name in (b'statusresponse', b'queryid'):
                    # \statusresponse\1 or \queryid\1
                    try:
                        packet_id = int(value)
                    # \queryid\gs1
                    except:
                        packet_id = 1
                elif name == b'final':
                    # packet_id should have already been picked up with the previous iteration
                    try:
                        assert packet_id is not None, 'packet_id is None'
                    except AssertionError as e:
                        raise base.ResponseMalformed(e)
                    else:
                        count = packet_id
            if packet_id is None:
                raise base.ResponseMalformed('failed to read packet id')
            ordered[packet_id] = packet
        return ordered, count

    def _parse_params(self, data):
        params = []
        split = data.split(b'\\')
        for i, name in enumerate(split):
            # skip values
            if not i % 2:
                continue
            try:
                # fetch the value
                params.append((name, split[i + 1]))
            except IndexError:
                pass
        return params