'''
Implementation of the pipe backend protocol version 3.
https://doc.powerdns.com/md/authoritative/backend-pipe/
'''
import sys
import logging

PIPE_ABI_VERSION = '3' # Version 3 adds EDNS support

def end():
    '''Send END answer'''
    sys.stdout.write('END\n')

def fail():
    '''Send FAIL answer'''
    sys.stdout.write('FAIL\n')

def handshake(line):
    '''Handshake for the protocol'''
    if line == 'HELO\t%s\n' % (PIPE_ABI_VERSION):
        sys.stdout.write('OK\t[pgwrr] Starting...\n')
        return True

    fail()
    return False

def query(line):
    '''Query format unpacking'''
    if line and line[:2] == 'Q\t':
        try:
            (dummy_q, qname, qclass, qtype, qid, rip, lip, edns) = line.strip().split('\t')
            # Respond to ANY requests with A
            if qtype == 'ANY':
                qtype = 'A'
            return (qname, qclass, qtype, qid, rip, lip, edns)
        except ValueError:
            logging.error('Cannot unpack query!')
            raise

    logging.error('Read a non query!')
    raise ValueError

# pylint: disable=too-many-arguments
def answer(qname, qclass, qtype, qcontent, qttl='3600', qid='-1', qscopebits='0', qauth='1'):
    '''Answer formatting
    Defaults:
       - ttl: 3600s
       - id:  -1      (ignored)
       - scopebits: 0 (ignored)
       - auth: 1      (always authoritative)
    '''
    if qname and qclass and qtype and qcontent:
        # Set scopebits to 0 and auth to 1 (default values)
        sys.stdout.write('DATA\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' %
                         (qscopebits, qauth, qname, qclass, qtype, qttl, qid, qcontent))
        end()
    else:
        logging.error('Bad answer or no data!')
        raise TypeError
