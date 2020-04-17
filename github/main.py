#!/usr/bin/env python3

import logging
import socket
import time

import requests

LOGGER = logging.getLogger('mierzyciel.github')

def get_github_status(org_name):
    url = f'https://api.github.com/orgs/{org_name}/repos'
    j = requests.get(url).json()
    return {
        'num_repos': len(j)
    }


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
    prefix = 'hakierspejs.github.'
    while True:
        h = ('graphite.hs-ldz.pl', 2003)
        stats = get_github_status('hakierspejs')
        for key, value in stats.items():
            upload_to_graphite(h, prefix + key, value)
        time.sleep(60)

if __name__ == '__main__':
    logging.basicConfig(level='INFO')
    main()
