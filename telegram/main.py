#!/usr/bin/env python

import logging
import socket
import urllib.request
import time

LOGGER = logging.getLogger('mierzyciel.telegram')

def get_telegram_stats(chat_name):
    s = urllib.request.urlopen('https://t.me/' + chat_name).read().decode()
    prefix = '<div class="tgme_page_extra">'
    line = [x for x in s.split('\n') if x.startswith(prefix)][0][len(prefix):]
    words = line.split()
    return int(words[0]), int(words[2])

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
        for chat in ['hakierspejs', 'hslodzbot']:
            stats = get_telegram_stats(chat)
            h = ('graphite.hs-ldz.pl', 2003)
            prefix = 'hakierspejs.telegram.' + chat + '.'
            upload_to_graphite(h, prefix + 'num_joined', stats[0])
            upload_to_graphite(h, prefix + 'num_active', stats[1])
        time.sleep(60)

if __name__ == '__main__':
    fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level='INFO', format=fmt)
    main()
