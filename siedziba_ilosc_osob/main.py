#!/usr/bin/env python

import time
import socket
import logging

import requests

LOGGER = logging.getLogger('siedziba_ilosc_osob.__main__')


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


def get_last_season():
    url = 'https://at.hs-ldz.pl/api/v1/users?online=true'
    return len(requests.get(url).json())


def main():
    prefix = 'hakierspejs.siedziba_ilosc_osob.'
    h = ('graphite.hs-ldz.pl', 2003)
    while True:
        last_season = get_last_season()
        upload_to_graphite(h, prefix + 'last_season', last_season)
        time.sleep(60.0)


if __name__ == '__main__':
    fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level='INFO', format=fmt)
    main()
