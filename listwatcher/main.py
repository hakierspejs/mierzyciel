#!/usr/bin/env python

import re
import os
import time
import socket
import logging

import requests
import lxml.html

LIST_URL = 'https://lists.hackerspace.pl/mailman/admin/lodz/members'
LOGGER = logging.getLogger('listwatcher.__main__')


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


def get_subscribed(admin_cookie):
    r = requests.get(LIST_URL, headers={'Cookie': admin_cookie})
    h = lxml.html.fromstring(r.text)
    return {
        e.strip() for e in h.xpath('//* [contains(., "@")]/text()') if '@' in e
    }


def list_archives():
    t = requests.get('https://lists.hackerspace.pl/pipermail/lodz/').text
    xpath = '//a [contains(@href, ".txt")]/@href'
    for x in lxml.html.fromstring(t).xpath(xpath):
        yield 'https://lists.hackerspace.pl/pipermail/lodz/' + x


def extract_email(email_desc):
    email = email_desc.split('(')[0].split('<')[-1].rstrip('>')
    for at_replacement in [' at ', ' w ']:
        email = email.replace(at_replacement, '@')
    return email.strip()


def get_active_in_archive(archive_url):
    t = requests.get(archive_url).text
    return {extract_email(x[1]) for x in re.findall('(\n\n)?From: (.*)\n', t)}


def get_active_ever():
    ret = set()
    for archive_url in list_archives():
        for active in get_active_in_archive(archive_url):
            ret.add(active)
    return ret


def main():
    admin_cookie = open(os.environ['MAILMAN_ADMIN_COOKIE_FPATH']).read()
    admin_cookie = admin_cookie.strip()
    prefix = 'hakierspejs.mailinglist.'
    h = ('graphite.hs-ldz.pl', 2003)
    while True:
        num_subscribed = len(get_subscribed(admin_cookie))
        num_active_ever = len(get_active_ever())
        upload_to_graphite(h, prefix + 'num_subscribed', num_subscribed)
        upload_to_graphite(h, prefix + 'active_ever', num_active_ever)
        time.sleep(60.0)


if __name__ == '__main__':
    main()
