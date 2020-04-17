#!/usr/bin/env python3

import logging
import socket
import time

import requests
import lxml.html

LOGGER = logging.getLogger('mierzyciel.telegram')

def get_num_facebook_likes(fb_name):
    url = f'https://www.facebook.com/{fb_name}'
    num_tries = 10
    for n in range(num_tries):
        try:
            h = lxml.html.fromstring(requests.get(url).text)
            x1 = '//div [contains(., "' + 'lubi' + '")]/text()'
            x2 = '//div [contains(., "' + 'like' + '")]/text()'
            s = (h.xpath(x1) or h.xpath(x2))[0].split()[0].strip()
            return int(s)
        except KeyError:
            if n == num_tries - 1:
                raise
        time.sleep(10.0)


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

def main():
    while True:
        h = ('graphite.hs-ldz.pl', 2003)
        likes = get_num_facebook_likes('hakierspejs')
        upload_to_graphite(h, 'hakierspejs.facebook.num_likes', likes)
        time.sleep(60)

if __name__ == '__main__':
    logging.basicConfig(level='INFO')
    main()
