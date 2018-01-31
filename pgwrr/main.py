'''
Main entry point for processing lines
'''
import pgwrr.proto
import pgwrr.db

def handshake(line):
    '''Pass this to proto'''
    return pgwrr.proto.handshake(line)

def geo(filename):
    '''Pass this to db'''
    return pgwrr.db.geoip(filename)

def conf(filename):
    '''Pass this to db'''
    return pgwrr.db.conf(filename)

def parse(geoip, zones, sites, line):
    '''Parse line using
        - MaxMind GeoIP City database
        - zones
        - sites
    '''
    # Unpack query
    try:
        qname, qclass, qtype, dummy_id, qremote_ip, dummy_localip, qedns = pgwrr.proto.query(line)
    except ValueError:
        pgwrr.proto.fail()
        return

    # Zone and site lookup
    qzone = pgwrr.db.zone(geoip, zones, qremote_ip, qedns)
    sites = pgwrr.db.site(sites, qname, qzone, qclass, qtype)

    error = False
    for rtype, rcontent, rttl in sites:
        try:
            pgwrr.proto.answer(qname, qclass, rtype, rcontent, rttl)
        except TypeError:
            error = True

    if error:
        pgwrr.proto.fail()
    else:
        pgwrr.proto.end()
