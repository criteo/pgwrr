'''
DNS site lookup
'''
import geoip2.database     # C parser by default, fallback to pure Python
import logging             # for logging
from random import randint # for weighted round robin
import socket, struct      # for IP validation
import yaml                # for configuration loading
try:
    from yaml import CLoader as Loader # load C parser
except ImportError:
    from yaml import Loader            # fallback to pure Python

def reserved(address):
    '''Test for valid IPv4 address and if it is reserved'''
    try:
        test_ip = struct.unpack('!I', socket.inet_pton(socket.AF_INET, address))[0]
    except socket.error:
        return True

    subnets = ([0xff000000, 0x00000000], # 0.0.0.0/8       "this" network
               [0xff000000, 0x0a000000], # 10.0.0.0/8      private
               [0xffc00000, 0x64400000], # 100.64.0.0/10   private
               [0xff000000, 0x7f000000], # 127.0.0.0/8     loopback
               [0xffff0000, 0xa9fe0000], # 169.254.0.0/16  link local
               [0xfff00000, 0xac100000], # 172.16.0.0/12   private
               [0xffffff00, 0xc0000000], # 192.0.0.0/24    reserved
               [0xffffff00, 0xc0000200], # 192.0.2.0/24    test
               [0xffffff00, 0xc0586300], # 192.88.99.0/24  6to4 anycast
               [0xffff0000, 0xc0a80000], # 192.168.0.0/16  private
               [0xfffe0000, 0xc6120000], # 198.18.0.0/15   reserved
               [0xffffff00, 0xc6336400], # 198.51.100.0/24 test
               [0xffffff00, 0xcb007100], # 203.0.113.0/24  test
               [0xe0000000, 0xe0000000]) # 224.0.0.0/3     multicast + future use

    for net in subnets:
        if test_ip & net[0] == net[1]:
            return True

    return False

def zone(georeader, zones, remoteip, edns='0.0.0.0/8'):
    '''Zone lookup using GeoIP2 City database

    The zones variable must be a dict abiding to the following rule:
      1. a key may be 'default' or an ISO 3166-1 alpha-2 country code
      2. there has to be one and only one key named 'default'
      3. the 'default' key must have a string value
      4. a key may have a string (zone to return) or a dict value
      5. in case of dict value:
        1. a key may be 'default' or the second part of an ISO 3166-2 code
        2. there has to be one and only one key named 'default'
        3. the 'default' key must have a string value

    Example (YAML syntax):
      'default': eu
      'FR':      eu
      'US':
        'default': us-east
        'CA':      us-west
    '''

    # Default zone to return is under 'default'
    default_zone = zones['default']

    # Get rid of netmask in edns
    edns = edns.split('/')[0]

    # If EDNS is reserved, pick the remote ip
    if reserved(edns):
        # If remote ip is reserved, return default zone
        if reserved(remoteip):
            logging.info('Reserved address: %s!', remoteip)
            return default_zone
        else:
            address = remoteip
    else:
        address = edns

    # Geolocate the address using GeoIPv2 City
    try:
        geo = georeader.city(address)
    except geoip2.errors.AddressNotFoundError:
        logging.warning('Address not found in GeoIP database: %s!', address)
        return default_zone

    # Get zone for given country code
    country = geo.country.iso_code
    gzone = zones.get(country, default_zone)

    # If the returned zone is a dict
    # return zone for given region code
    if isinstance(gzone, dict):
        # Get zone for given region code
        region = geo.subdivisions.most_specific.iso_code
        default_zone = zones[country]['default']

        return gzone.get(region, default_zone)
    else:
        return gzone

def site(sites, qname, qzone, qclass='IN', qtype='A'):
    '''Site lookup returns (ip, ttl)

    The sites variable must be a dict abiding to the following format:
    <fqdn>:
      <class>:
        <type>:
          content:
            <zone>:
              <ip>: <weight>

    <fqdn>   - may be a FQDN or a DNS wildcard
    <class>  - a DNS class
    <type>   - a DNS type
    <zone>   - a string, there has to be one 'default' key
    <ip>     - an IP
    <weight> - a number representing the weight for weighted round robin

    Example (in YAML format):
      www.example.com:
        IN:
          A:
            content:
              default:
                1.1.1.1: 20
                2.2.2.2: 80
              us:
                3.3.3.3: 100
      '*.example.com':
        IN:
          A:
            content:
              default:
                1.1.1.1: 100
    '''

    # Literal site check
    if qname in sites:
        pass
    else:
        # Wildcard site check
        wildcard = '*' + qname[qname.find('.'):]
        if wildcard in sites:
            qname = wildcard
        else:
            logging.warning('No such site: %s!', qname)
            return (None, None)

    # Faster than get for nested hashes
    try:
        mname = sites[qname][qclass][qtype]
    except KeyError:
        logging.warning('No match for: %s %s %s!', qname, qclass, qtype)
        return (None, None)

    # Get ttl or default
    mttl = mname.get('ttl', 3600)
    # Get content by zone or default
    mcontent = mname['content'].get(qzone, mname['content']['default'])

    # Weighted round robin algorithm
    if len(mcontent) > 1:
        # Create a random integer between 1 the total sum
        rnd = randint(1, sum(mcontent.values()))
        upto = 0
        # Get weighted random address
        for address in sorted(mcontent):
            if rnd <= upto + mcontent[address]:
                return (address, mttl)
            upto += mcontent[address]
    # Only one result
    else:
        return (mcontent.keys()[0], mttl)

def geoip(filename):
    '''Load MaxMindDB'''
    reader = geoip2.database.Reader(filename)
    return reader

def conf(filename):
    '''Load configuration from YAML'''
    with open(filename, 'r') as stream:
        parsed = yaml.load(stream, Loader)
    return parsed
