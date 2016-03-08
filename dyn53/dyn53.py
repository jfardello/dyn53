#!/usr/bin/env python3
'''
Simple tool for updating amazon route53 DNS entres "ala dyndns".
It requires boto, requests, and dnspython, and certifi.

Install
-------
    sudo pip install boto requests dnspython
    vi ~/.boto 

        ;http://docs.pythonboto.org/en/latest/boto_config_tut.html
        [Credentials]
        aws_access_key_id = <your_access_key_here>
        aws_secret_access_key = <your_secret_key_here>

    vi dynroute.py 
        # Just edit region, ttl, domain, and may be USE_COMTREND and 
        # COMTREND_* stuf.


Usage
-----
    dyn53 [-h] [-a ADDRESS] [-d DOMAIN] [-s SUBDOMAIN] [-t TTL]

    With no parameters the script will use the host nodename and the 
    configured domain and TTL in the [dyn53] section of the boto config.

    [dyn53]
    domain = 'domain.tld.'
    region = 'eu-west-1'
    TTL = 300


'''
import sys
from argparse import ArgumentParser
from datetime import datetime
import platform
import logging
import os

from boto import route53
import requests
from dns import resolver
from dns.resolver import NoAnswer, NXDOMAIN
import certifi
 
domain = 'domain.tld.'
region = 'eu-west-1'
TTL = 300


def get_subdomain():
    return platform.node().split(".")[0]

def get_public_ip():
    addr = requests.get('https://api.ipify.org', cert=(certifi.where(),))
    return addr.text.rstrip()

def check(subdomain, domain, addr, logger):
    #bypass what our dns says and ask directly to the autority.
    zresolver = resolver.Resolver()
    try:
        for each in resolver.query(domain, 'NS'):
            ns_srv = resolver.query(each.to_text())[0].to_text()
            zresolver.nameservers.append(ns_srv)
        res = zresolver.query("%s.%s" % (subdomain, domain), 'A')[0].to_text()
        return res == addr
    except (NoAnswer, NXDOMAIN):
        logger.error("Can't resolve!")
        return False

def update(address, subdomain=None, domain=domain, ttl=TTL, debug=False):
    logger = logging.getLogger('dyn53')

    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
        
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.debug('Domain is %s', domain)

    if address is None:
        address = get_public_ip()
    #Lazy check, don't connect to r53 if it isn't needed.
    if check(subdomain, domain, address, logger):
        logger.debug('FQDN is already pointing to %s', address)
        sys.exit(0)

    logger.debug('Region is %s', region)
    conn = route53.connect_to_region(region)
    zone = conn.get_zone(domain)
    logger.debug('Got zone: %s', zone)
    
    if subdomain is None:
        subdomain = get_subdomain()

    fqdn = '%s.%s' % (subdomain, domain)
    logger.debug('FQDN is: %s', fqdn)

    address_r = zone.get_a(fqdn)
    if address_r:
        old_value = address_r.resource_records[0]
         
        if old_value == address:
            logger.info('Anchor for %s already there.. (%s)' % (fqdn, address))
            sys.exit(0)
    
        logger.info('Updating %s: %s -> %s' % (fqdn, old_value, address))
        try:
            zone.update_a(fqdn, address, ttl)
         
        except route53.exception.DNSServerError:
            # There was no record, let's add one.
            zone.add_a(fqdn, address, TTL)
    else:
        logger.info('Adding new record, (%s, %s, ttl:%s)', fqdn, address, ttl)
        zone.add_a(fqdn, address, ttl)

def cli():
    subdomain = get_subdomain()
    parser = ArgumentParser(description='route53 dynamic IP address updater')
    parser.add_argument('-a', '--address', help='force this address.',
            default=None)
    parser.add_argument('-d', '--domain', default=domain,
            help='Use this domain. Defaults to "%s")' % domain)
    parser.add_argument('-s', '--subdomain', default=subdomain,
            help='Use this subdomain, Defaults to "%s."' % subdomain)
    parser.add_argument('-t', '--ttl', default=TTL,
            help='Time to live (TTL), defaults to "%s."' % TTL)
    parser.add_argument('-D', '--debug', default=False, action='store_true',
            help="Enable debug messages")
    args = parser.parse_args()

    update(args.address, subdomain=args.subdomain, domain=args.domain, 
            ttl=args.ttl, debug=args.debug)

if __name__ == '__main__':
    cli()
