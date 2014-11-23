# coding: utf-8
import unittest
import collections
import mock

from serverquery.exceptions import ResponseIncomplete, ResponseMalformed
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

        self.assertEqual(params['hostname'], u'[C=FF0000][c=33CCCC]>|S[C=FFFFFF]S|<[c=ffff00]Arg[C=ffffff]en[c=33CCCC]tina®[c=ff0000]-By FNXgaming.com')
        self.assertEqual(params['hostport'], u'10780')
        self.assertEqual(params['kills_4'], u'14')
        self.assertEqual(params['kills_5'], u'3')
        self.assertEqual(params['arrests_8'], u'2')
        self.assertEqual(params['queryid'], u'AMv1')
        self.assertEqual(params['ping_0'], u'67')
        self.assertEqual(params['score_2'], u'1')

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
        params = self.server.format_response(self.server.format_packets(packets))

        self.assertEqual(params['hostname'], u'{FAB} Clan Server')
        self.assertEqual(params['hostport'], u'10580')
        self.assertEqual(params['score_0'], u'0')
        self.assertEqual(params['ping_3'], u'163')
        self.assertEqual(params['kills_12'], u'2')
        self.assertEqual(params['queryid'], u'AMv1')
        self.assertEqual(params['final'], u'')

    def test_response_incomplete(self):
        response = [
            b'\\hostname\\test\\queryid\\1',
            b'\\hostport\\10480\\queryid\\2',
        ]
        with self.assertRaises(ResponseIncomplete):
            self.server.parse_packets(response)

    def test_response_malformed(self):
        response = [
            b'\\hostname\\test\\hostport\\10480\\final\\',
        ]
        with self.assertRaises(ResponseMalformed):
            self.server.parse_packets(response)

    def test_vanilla_queryid_is_not_integer(self):
        response = [
            b'\\hostname\\test\\hostport\\10480\\queryid\\gs1\\final\\',
        ]
        sorted, count = self.server._sort_packets(response)
        self.assertEqual(count, 1)

    def test_queryid_is_not_zero_based(self):
        response = [
            b'\\hostname\\test\\queryid\\1',
            b'\\hostport\\10480\\queryid\\2\\final\\',
        ]
        sorted, count = self.server._sort_packets(response)
        self.assertEqual(count, 2)

    def test_statusresponse_is_zero_based(self):
        response = [
            b'\\statusresponse\\0\\hostname\\test\\queryid\\AMv1\\eof\\',
            b'\\statusresponse\\1\\queryid\\AMv1\\final\\\\eof\\',
        ]
        sorted, count = self.server._sort_packets(response)
        self.assertEqual(count, 2)

    def test_statusresponse_eof_removed_from_response_final_queryid_are_not(self):
        response = [
            b'\\statusresponse\\0\\hostname\\test\\queryid\\AMv1\\final\\\\eof\\'
        ]
        packets = self.server.parse_packets(response)
        params = dict(self.server.format_packets(packets))

        self.assertNotIn('statusresponse', params)
        self.assertNotIn('eof', params)
        self.assertIn('queryid', params)
        self.assertIn('final', params)

    def test_gs1_response(self):
        response =  [
            b'\\player_3\\Morgan\\score_3\\6\\ping_3\\53\\team_3\\1\\kills_3\\6\\deaths_3\\7'
            b'\\arrested_3\\1\\player_4\\Jericho\\score_4\\3\\ping_4\\46\\team_4\\0\\kills_4\\3'
            b'\\deaths_4\\12\\player_5\\Bolint\\score_5\\21\\ping_5\\57\\team_5\\1\\kills_5\\16'
            b'\\deaths_5\\8\\arrests_5\\1\\player_6\\FsB\\score_6\\2\\ping_6\\46\\team_6\\1\\kills_6\\5'
            b'\\deaths_6\\10\\tkills_6\\1\\arrested_6\\1\\player_7\\t00naab\\score_7\\11\\ping_7\\27'
            b'\\team_7\\0\\kills_7\\11\\vip_7\\1\\player_8\\ob\\score_8\\2\\ping_8\\74\\team_8\\1'
            b'\\kills_8\\2\\deaths_8\\3\\player_9\\martino\\score_9\\5\\ping_9\\67\\team_9\\1\\queryid\\2',

            b'\\hostname\\-==MYT Team Svr==-\\numplayers\\13\\maxplayers\\16'
            b'\\gametype\\VIP Escort\\gamevariant\\SWAT 4\\mapname\\Fairfax Residence'
            b'\\hostport\\10480\\password\\false\\gamever\\1.1\\round\\5\\numrounds\\5'
            b'\\timeleft\\286\\timespecial\\0\\swatscore\\41\\suspectsscore\\36\\swatwon'
            b'\\1\\suspectswon\\2\\player_0\\ugatz\\score_0\\0\\ping_0\\43\\team_0\\1'
            b'\\deaths_0\\9\\player_1\\|CSI|Miami\\score_1\\8\\ping_1\\104\\team_1\\0'
            b'\\kills_1\\8\\deaths_1\\4\\player_2\\aphawil\\score_2\\7\\ping_2\\69'
            b'\\team_2\\0\\kills_2\\8\\deaths_2\\11\\tkills_2\\2\\arrests_2\\1\\queryid\\1',

            b'\\kills_9\\5\\deaths_9\\2\\player_10\\conoeMadre\\score_10\\7\\ping_10\\135\\team_10\\0'
            b'\\kills_10\\7\\deaths_10\\2\\player_11\\Enigma51\\score_11\\0\\ping_11\\289\\team_11\\0'
            b'\\deaths_11\\1\\player_12\\Billy\\score_12\\0\\ping_12\\999\\team_12\\0\\queryid\\3\\final\\'
        ]

        packets = self.server.parse_packets(response)
        params = self.server.format_response(self.server.format_packets(packets))

        self.assertEqual(params['hostname'], u'-==MYT Team Svr==-')
        self.assertEqual(params['suspectsscore'], u'36')
        self.assertEqual(params['score_12'], u'0')
        self.assertEqual(params['player_3'], u'Morgan')
        self.assertEqual(params['ping_12'], u'999')
        self.assertEqual(params['final'], u'')

    def test_ammod_serverquery_response(self):
        response = [
            # last packet comes first and so forth
            b'\\statusresponse\\2\\kills_13\\1\\kills_14\\1\\deaths_1\\1\\deaths_2\\1\\deaths_4\\1\\deaths_5\\1'
            b'\\deaths_9\\1\\deaths_14\\1\\queryid\\AMv1\\final\\\\eof\\',

            # key, value of score_0 from statusresponse=0 have been split
            b'\\statusresponse\\1\\0\\score_1\\0\\score_2\\1\\score_3\\0\\score_4\\0\\score_5\\0\\score_6\\0'
            b'\\score_7\\0\\score_8\\1\\score_9\\0\\score_10\\0\\score_11\\0\\score_12\\2\\score_13\\1'
            b'\\score_14\\1\\ping_0\\155\\ping_1\\127\\ping_2\\263\\ping_3\\163\\ping_4\\111\\ping_5\\117\\ping_6'
            b'\\142\\ping_7\\121\\ping_8\\159\\ping_9\\142\\ping_10\\72\\ping_11\\154\\ping_12\\212\\ping_13'
            b'\\123\\ping_14\\153\\team_0\\1\\team_1\\0\\team_2\\1\\team_3\\0\\team_4\\0\\team_5\\0\\team_6\\1'
            b'\\team_7\\1\\team_8\\0\\team_9\\0\\team_10\\0\\team_11\\1\\team_12\\1\\team_13\\0\\team_14\\1'
            b'\\kills_2\\1\\kills_8\\1\\kills_12\\2\\eof\\',

            b'\\statusresponse\\0\\hostname\\{FAB} Clan Server\\numplayers\\15\\maxplayers'
            b'\\16\\gametype\\VIP Escort\\gamevariant\\SWAT 4\\mapname\\Red Library Offices'
            b'\\hostport\\10580\\password\\0\\gamever\\1.0\\statsenabled\\0\\swatwon\\1\\suspectswon\\0'
            b'\\round\\2\\numrounds\\7\\player_0\\{FAB}Nikki_Sixx<CPL>\\player_1\\Nico^Elite\\player_2'
            b'\\Balls\\player_3\\\xab|FAL|\xdc\xee\xee\xe4^\\player_4\\Reynolds\\player_5\\4Taws\\player_6'
            b'\\Daro\\player_7\\Majos\\player_8\\mi\\player_9\\tony\\player_10\\MENDEZ\\player_11\\ARoXDeviL'
            b'\\player_12\\{FAB}Chry<CPL>\\player_13\\P\\player_14\\xXx\\score_0\\eof\\',
        ]

        packets = self.server.parse_packets(response)
        params = self.server.format_response(self.server.format_packets(packets))

        self.assertEqual(params['hostname'], u'{FAB} Clan Server')
        self.assertEqual(params['hostport'], u'10580')
        self.assertEqual(params['score_0'], u'0')
        self.assertEqual(params['ping_3'], u'163')
        self.assertEqual(params['kills_12'], u'2')
        self.assertEqual(params['player_13'], u'P')
        self.assertEqual(params['queryid'], u'AMv1')
        self.assertEqual(params['final'], u'')
