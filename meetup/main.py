#!/usr/bin/env python

import re
import os
import time
import socket
import logging
import urllib.parse

import requests
import lxml.html

LOGGER = logging.getLogger('meetup.__main__')


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


def get_num_subscribed(group_name):
    url = 'https://www.meetup.com/' + urllib.parse.quote(group_name)
    h = lxml.html.fromstring(requests.get(url).text)
    return int(h.xpath('//span [contains(.,"members")]/text()')[0].split()[0])


def main():
    prefix = 'hakierspejs.meetup.'
    h = ('graphite.hs-ldz.pl', 2003)
    while True:
        num_subscribed = get_num_subscribed('Hakierspejs-Łódź')
        upload_to_graphite(h, prefix + 'num_subscribed', num_subscribed)
        time.sleep(60.0)


if __name__ == '__main__':
    fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level='INFO', format=fmt)
    main()
