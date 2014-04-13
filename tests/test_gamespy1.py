import unittest
import collections
import mock

from serverquery.protocol import gamespy1


class ParserTestCase(unittest.TestCase):

    def setUp(self):
        self.server = gamespy1.Server('127.0.0.1', 10481)

    def test_response1(self):
        response = [
            b'\\statusresponse\\0\\hostname\\[C=FF0000][c=33CCCC]>|S[C=FFFFFF]S|<[c=ffff00]Arg[C=ffffff]en[c=33CCCC]tina\xc2\xae[c=ff0000]-By FNXgaming.com'
            b'\\numplayers\\10\\maxplayers\\16\\gametype\\Barricaded Suspects\\gamevariant\\SWAT 4\\' 
            b'mapname\\A-Bomb Nightclub\\hostport\\10780\\password\\0\\gamever\\1.0\\statsenabled\\0\\swatwon\\2\\suspectswon\\0'
            b'\\round\\3\\numrounds\\3\\player_0\\darwinn\\player_1\\kyle\\player_2\\super\\player_3\\\xab|FAL|cucuso\\player_4\\'
            b'||AT||Lp!\\player_5\\Diejack1\\player_6\\Player1232\\player_7\\Mojojojo\\player_8\\DrLemonn\\player_9\\elmatap\\score_0\\4\\eof\\', 

            b'\\statusresponse\\1\\score_1\\2\\score_2\\1\\score_3\\10\\score_4\\14\\score_5\\-3\\score_6\\11\\score_7\\25\\score_8\\18\\score_9\\5\\'
            b'ping_0\\67\\ping_1\\184\\ping_2\\265\\ping_3\\255\\ping_4\\54\\ping_5\\218\\ping_6\\208\\ping_7\\136\\ping_8\\70\\ping_9\\64\\team_0\\0'
            b'\\team_1\\0\\team_2\\1\\team_3\\0\\team_4\\1\\team_5\\0\\team_6\\1\\team_7\\1\\team_8\\0\\team_9\\0\\kills_0\\4\\kills_1\\2\\kills_2\\1'
            b'\\kills_3\\5\\kills_4\\14\\kills_5\\3\\kills_6\\6\\kills_7\\10\\kills_8\\8\\kills_9\\6\\tkills_5\\2\\tkills_9\\2\\deaths_0\\6\\deaths_1\\9'
            b'\\deaths_2\\4\\deaths_3\\4\\deaths_4\\8\\deaths_5\\4\\deaths_6\\7\\eof\\', 

            b'\\statusresponse\\2\\deaths_7\\5\\deaths_8\\7\\deaths_9\\4'
            b'\\arrests_3\\1\\arrests_6\\1\\arrests_7\\3\\arrests_8\\2\\arrests_9'
            b'\\1\\arrested_1\\1\\arrested_2\\2\\arrested_4\\1\\arrested_5\\1\\arrested_6\\1'
            b'\\arrested_9\\2\\queryid\\AMv1\\final\\\\eof\\'
        ]

        packets = self.server.parse_packets(response)
        packets = self.server.format_packets(packets)
        params = dict(packets)

        self.assertEqual(params['hostname'], '[C=FF0000][c=33CCCC]>|S[C=FFFFFF]S|<[c=ffff00]Arg[C=ffffff]en[c=33CCCC]tina®[c=ff0000]-By FNXgaming.com')
        self.assertEqual(params['hostport'], '10780')
        self.assertEqual(params['kills_4'], '14')
        self.assertEqual(params['kills_5'], '3')
        self.assertEqual(params['arrests_8'], '2')
        self.assertEqual(params['queryid'], 'AMv1')
        self.assertEqual(params['ping_0'], '67')
        self.assertEqual(params['score_2'], '1')

    def test_response2(self):
        response = [
            b'\\statusresponse\\0\\hostname\\{FAB} Clan Server\\numplayers\\15\\maxplayers'
            b'\\16\\gametype\\VIP Escort\\gamevariant\\SWAT 4\\mapname\\Red Library Offices'
            b'\\hostport\\10580\\password\\0\\gamever\\1.0\\statsenabled\\0\\swatwon\\1\\suspectswon\\0'
            b'\\round\\2\\numrounds\\7\\player_0\\{FAB}Nikki_Sixx<CPL>\\player_1\\Nico^Elite\\player_2'
            b'\\Balls\\player_3\\\xab|FAL|\xdc\xee\xee\xe4^\\player_4\\Reynolds\\player_5\\4Taws\\player_6'
            b'\\Daro\\player_7\\Majos\\player_8\\mi\\player_9\\tony\\player_10\\MENDEZ\\player_11\\ARoXDeviL'
            b'\\player_12\\{FAB}Chry<CPL>\\player_13\\P\\player_14\\xXx\\score_0\\0\\eof\\',

            b'\\statusresponse\\1\\score_1\\0\\score_2\\1\\score_3\\0\\score_4\\0\\score_5\\0\\score_6\\0'
            b'\\score_7\\0\\score_8\\1\\score_9\\0\\score_10\\0\\score_11\\0\\score_12\\2\\score_13\\1'
            b'\\score_14\\1\\ping_0\\155\\ping_1\\127\\ping_2\\263\\ping_3\\163\\ping_4\\111\\ping_5\\117\\ping_6'
            b'\\142\\ping_7\\121\\ping_8\\159\\ping_9\\142\\ping_10\\72\\ping_11\\154\\ping_12\\212\\ping_13'
            b'\\123\\ping_14\\153\\team_0\\1\\team_1\\0\\team_2\\1\\team_3\\0\\team_4\\0\\team_5\\0\\team_6\\1'
            b'\\team_7\\1\\team_8\\0\\team_9\\0\\team_10\\0\\team_11\\1\\team_12\\1\\team_13\\0\\team_14\\1'
            b'\\kills_2\\1\\kills_8\\1\\kills_12\\2\\eof\\',

            b'\\statusresponse\\2\\kills_13\\1\\kills_14\\1\\deaths_1\\1\\deaths_2\\1\\deaths_4\\1\\deaths_5\\1'
            b'\\deaths_9\\1\\deaths_14\\1\\queryid\\AMv1\\final\\\\eof\\',
        ]

        packets = self.server.parse_packets(response)
        packets = self.server.format_packets(packets)
        params = dict(packets)

        #self.assertEqual(params['hostname'], '{FAB} Clan Server')
        self.assertEqual(params['hostport'], '10580')
        self.assertEqual(params['score_0'], '0')
        self.assertEqual(params['ping_3'], '163')
        self.assertEqual(params['kills_12'], '2')
        self.assertEqual(params['queryid'], 'AMv1')
        self.assertEqual(params['final'], '')
