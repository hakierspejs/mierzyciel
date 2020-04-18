#!/usr/bin/env python

import re
import os
import time
import socket
import struct
import logging
import urllib.parse

LOGGER = logging.getLogger('mumble.__main__')


def upload_to_graphite(h, metric, value):
    s = socket.socket()
    try:
        s.connect(h)
        now = int(time.time())
        buf = f'{metric} {value} {now}\n'.encode()
        LOGGER.info('Sending %r to %r', buf, h)
        s.send(buf)
        s.close()
    except (ConnectionRefusedError, socket.timeout) as e:
        LOGGER.exception(e)
    time.sleep(3.0)


def get_mumble_user_count(mumble_server):
    '''Sends a PING to a given Mumble server and returns the number of
    Mumble users that are currently online. Returns zero on error.'''
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((mumble_server, 64738))
        s.send(b'\x00\x00\x00\x00abcdefgh')
        x = s.recv(1024)
        return struct.unpack('>xxxx' + 'x' * len('abcdefgh') + 'I' * 3, x)[0]
    except socket.error as e:
        LOGGER.error('get_mumble_user_count: %r', e)
        return 0


def main():
    prefix = 'hakierspejs.mumble.'
    h = ('graphite.hs-ldz.pl', 2003)
    while True:
        num_joined = get_mumble_user_count('junkcc.net')
        upload_to_graphite(h, prefix + 'num_joined', num_joined)
        time.sleep(60.0)


if __name__ == '__main__':
    fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level='INFO', format=fmt)
    main()
