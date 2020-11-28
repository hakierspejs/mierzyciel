#!/usr/bin/env python

import time
import socket
import logging

import requests
import lxml.html

LOGGER = logging.getLogger('temperatura.__main__')


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


def get_degrees_celcius():
    url = 'http://85.89.178.82:1060/'
    h = lxml.html.fromstring(requests.get(url).text)
    return float(h.xpath('//p[2]/text()')[0].strip().split(' ')[0])


def main():
    prefix = 'hakierspejs.temperatura.'
    h = ('graphite.hs-ldz.pl', 2003)
    while True:
        degrees_celcius = get_degrees_celcius()
        upload_to_graphite(h, prefix + 'degrees_celcius', degrees_celcius)
        time.sleep(60.0)


if __name__ == '__main__':
    fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level='INFO', format=fmt)
    main()
