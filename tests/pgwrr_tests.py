'''Main testing file'''
import pgwrr.proto
import pgwrr.db
import pgwrr.main

import geoip2.database
import StringIO
from mock import patch
from nose.tools import assert_equal, assert_in, assert_raises

def test_handshake():
    '''Test handshake'''
    with patch('sys.stdout', new=StringIO.StringIO()) as output:

        assert_equal(pgwrr.proto.handshake(''), False)
        assert_equal(output.getvalue(), 'FAIL\n')
        output.truncate(0) # Truncate output buffer

        assert_equal(pgwrr.proto.handshake('HELO\t1\n'), False)
        assert_equal(output.getvalue(), 'FAIL\n')
        output.truncate(0) # Truncate output buffer

        assert_equal(pgwrr.proto.handshake('HELO\t2\n'), False)
        assert_equal(output.getvalue(), 'FAIL\n')
        output.truncate(0) # Truncate output buffer

        assert_equal(pgwrr.proto.handshake('HELO\t3\n'), True)
        assert_equal(output.getvalue()[:3], 'OK\t')
        output.truncate(0) # Truncate output buffer

        assert_equal(pgwrr.proto.handshake('HELO\t4\n'), False)
        assert_equal(output.getvalue(), 'FAIL\n')
        output.truncate(0) # Truncate output buffer

def test_query():
    '''Test queries'''
    assert_raises(ValueError, pgwrr.proto.query, '')
    assert_raises(ValueError, pgwrr.proto.query, 'test\n')
    assert_raises(ValueError, pgwrr.proto.query, 'Q\t')
    assert_raises(ValueError, pgwrr.proto.query, 'Q\ta\n')
    assert_raises(ValueError, pgwrr.proto.query, 'R\ta\tb\tc\td\te\tf\tg\n')
    assert_equal(
        pgwrr.proto.query('Q\tname\tclass\ttype\tid\tip\tip\tedns\n'),
        ('name', 'class', 'type', 'id', 'ip', 'ip', 'edns')
    )
    # test mixed case query
    assert_equal(
        pgwrr.proto.query('Q\tnAmE\tclass\ttype\tid\tip\tip\tedns\n'),
        ('name', 'class', 'type', 'id', 'ip', 'ip', 'edns')
    )

def test_answer():
    '''Test answers'''
    with patch('sys.stdout', new=StringIO.StringIO()) as output:
        assert_equal(pgwrr.proto.answer(qname='name', qclass='IN', qtype='A',
                                        qcontent='10.0.0.1', qttl='60',
                                        qid='1'), None)
        assert_equal(output.getvalue(), 'DATA\t0\t1\tname\tIN\tA\t60\t1\t10.0.0.1\nEND\n')
        output.truncate(0) # Truncate output buffer

        assert_equal(pgwrr.proto.answer('localhost', 'IN', 'A', '127.0.0.1'), None)
        assert_equal(output.getvalue(), 'DATA\t0\t1\tlocalhost\tIN\tA\t3600\t-1\t127.0.0.1\nEND\n')
        output.truncate(0) # Truncate output buffer

        assert_raises(TypeError, pgwrr.proto.answer, '', 'IN', 'A', '127.0.0.1')

def test_reserved():
    '''Test ip checking'''
    assert_equal(pgwrr.db.reserved('whatever'), True)
    assert_equal(pgwrr.db.reserved('127.0'), True)
    assert_equal(pgwrr.db.reserved('0.0.0.0'), True)
    assert_equal(pgwrr.db.reserved('10.0.0.0'), True)
    assert_equal(pgwrr.db.reserved('100.64.0.0'), True)
    assert_equal(pgwrr.db.reserved('127.0.0.0'), True)
    assert_equal(pgwrr.db.reserved('169.254.0.0'), True)
    assert_equal(pgwrr.db.reserved('172.16.0.0'), True)
    assert_equal(pgwrr.db.reserved('192.0.0.0'), True)
    assert_equal(pgwrr.db.reserved('192.0.2.0'), True)
    assert_equal(pgwrr.db.reserved('192.168.0.0'), True)
    assert_equal(pgwrr.db.reserved('198.18.0.0'), True)
    assert_equal(pgwrr.db.reserved('198.51.100.0'), True)
    assert_equal(pgwrr.db.reserved('203.0.113.0'), True)
    assert_equal(pgwrr.db.reserved('224.0.0.0'), True)
    assert_equal(pgwrr.db.reserved('128.101.101.101'), False)

def test_zone_lookup():
    '''Test zone lookups'''
    georeader = geoip2.database.Reader('geoip/GeoLite2-City.mmdb')
    zones = {'default': 'as',
             'US': {'default': 'ny', 'CA': 'sv'},
             'HR': 'eu'}

    assert_equal(pgwrr.db.zone(georeader, zones, '127.0.0.1'), 'as')
    assert_equal(pgwrr.db.zone(georeader, zones, '192.168.0.1'), 'as')

    # FER, University of Zagreb
    assert_equal(pgwrr.db.zone(georeader, zones, '161.53.72.15'), 'eu')
    # DotCom Monitor
    assert_equal(pgwrr.db.zone(georeader, zones, '65.49.22.66'), 'sv')
    # IP in US with no region
    assert_equal(pgwrr.db.zone(georeader, zones, '23.23.23.23'), 'ny')
    # Test EDNS
    assert_equal(pgwrr.db.zone(georeader, zones, '8.8.8.8', '161.53.0.0/16'), 'eu')

def test_site_lookup():
    '''Test site lookups'''
    sites = {
        'www.example.com': {
            'IN': {
                'A': {
                    'ttl': 300,
                    'content': {
                        'default': {'0.0.0.1': 100},
                        'eu':      {'0.0.0.2': 100}
                        }
                    }
                }
            },
        '*.example.com': {
            'IN': {
                'A': {
                    'content': {
                        'default': {'0.0.0.3': 100},
                        'eu':      {'0.0.0.4': 100}
                        }
                    }
                }
            },
        'www.wrr.com': {
            'IN': {
                'A': {
                    'ttl': 300,
                    'content': {
                        'default': {'0.0.0.1': 50,
                                    '0.0.0.2': 50},
                        'eu': {'0.0.0.1': 25,
                               '0.0.0.2': 25,
                               '0.0.0.3': 25,
                               '0.0.0.4': 25}
                        }
                    }
                }
            }
        }
    assert_equal(pgwrr.db.site(sites, 'www.nonexistant.com', 'nonexistant'), (None, None))

    assert_equal(pgwrr.db.site(sites, 'www.example.com', 'nonexistant', 'CH', 'A'), (None, None))
    assert_equal(pgwrr.db.site(sites, 'www.example.com', 'nonexistant', 'IN', 'MX'), (None, None))
    assert_equal(pgwrr.db.site(sites, 'www.example.com', 'nonexistant'), ('0.0.0.1', 300))
    assert_equal(pgwrr.db.site(sites, 'www.example.com', 'eu'), ('0.0.0.2', 300))

    assert_equal(pgwrr.db.site(sites, 'test.example.com', 'nonexistant'), ('0.0.0.3', 3600))
    assert_equal(pgwrr.db.site(sites, 'test.example.com', 'eu'), ('0.0.0.4', 3600))

    assert_in(pgwrr.db.site(sites, 'www.wrr.com', 'ap'), (('0.0.0.1', 300), ('0.0.0.2', 300)))
    assert_in(pgwrr.db.site(sites, 'www.wrr.com', 'eu'), (
        ('0.0.0.1', 300), ('0.0.0.2', 300), ('0.0.0.3', 300), ('0.0.0.4', 300)))

def test_main():
    '''Test main entry point'''

    geoip = geoip2.database.Reader('geoip/GeoLite2-City.mmdb')
    zones = {'default': 'as',
             'HR': 'eu'}
    sites = {
        'www.example.com': {
            'IN': {
                'A': {
                    'ttl': 300,
                    'content': {
                        'default': {'0.0.0.1': 100},
                        'eu':      {'0.0.0.2': 100}
                        }
                    }
                }
            }
        }
    with patch('sys.stdout', new=StringIO.StringIO()) as output:

        assert_equal(pgwrr.main.parse(geoip, zones, sites, ''), None)
        assert_equal(output.getvalue(), 'FAIL\n')
        output.truncate(0) # Truncate output buffer

        assert_equal(pgwrr.main.parse(
            geoip, zones, sites,
            'Q\twww.example.com\tIN\tA\t1\t127.0.0.1\t127.0.0.1\t127.0.0.1'), None)
        assert_equal(output.getvalue(),
                     'DATA\t0\t1\twww.example.com\tIN\tA\t300\t-1\t0.0.0.1\nEND\n')
        output.truncate(0) # Truncate output buffer

        assert_equal(pgwrr.main.parse(
            geoip, zones, sites,
            'Q\twww.example.com\tIN\tA\t1\t127.0.0.1\t127.0.0.1\t161.53.72.15'), None)
        assert_equal(output.getvalue(),
                     'DATA\t0\t1\twww.example.com\tIN\tA\t300\t-1\t0.0.0.2\nEND\n')
        output.truncate(0) # Truncate output buffer

        assert_equal(pgwrr.main.parse(
            geoip, zones, sites,
            'Q\twww.example.com\tIN\tMX\t1\t127.0.0.1\t127.0.0.1\t161.53.72.15'), None)
        assert_equal(output.getvalue(), 'END\n')
        output.truncate(0) # Truncate output buffer
