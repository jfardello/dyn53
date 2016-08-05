"""
Simple tool for updating amazon route53 DNS entries "ala dyndns".
It requires boto3, requests, dnspython, and certifi.


Usage
-----
    dyn53 [-h] [-a ADDRESS] [-d DOMAIN] [-s SUBDOMAIN] [-t TTL]

    With no parameters the script will use the host's node-name and the
    configured domain and TTL in the [dyn53] section of ~/.config/dyn53.cfg

    [dyn53]
    hosted_zone_id = My hosted Zone Id
    domain = domain.tld.
    ttl = 300
    debug = False
    aws_sec_key = MY SECRET KEY
    aws_key = MY KEY


"""
import sys
import logging
import platform


import boto3
from botocore.exceptions import ClientError
import requests
from dns import resolver
from dns.resolver import NoAnswer, NXDOMAIN
import certifi

from .conf import Conf, cli, WrongPermissions


logger = logging.getLogger('dyn53')
ch = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.INFO)


def get_public_ip():
    address = requests.get('https://api.ipify.org', verify=certifi.where())
    return address.text.rstrip()


def check(subdomain, domain, addr):
    """ Bypass what our dns says and ask directly to the authority.

    zresolver is passed by kwarg to allow overriding in the tests.
    """
    zresolver = resolver.Resolver()
    try:
        for each in resolver.query(domain, 'NS'):

            ns_srv = resolver.query(each.to_text())[0].to_text()
            zresolver.nameservers.clear()
            zresolver.nameservers.append(ns_srv)
        res = zresolver.query("%s.%s" % (subdomain, domain), 'A')[0].to_text()
        return res == addr
    except (NoAnswer, NXDOMAIN):
        logger.error("Can't resolve!")
        return False


def update(address, subdomain, domain, ttl, conf, debug=False,):
    """See if we need to call boto.client().change_resource_record_set """
    if debug:
        logger.setLevel(logging.DEBUG)

    if address is None:
        address = get_public_ip()

    logger.debug("Got ip: %s", address)

    # Lazy check, don't connect to r53 if it isn't needed.
    if check(subdomain, domain, address):
        logger.debug('FQDN is already pointing at %s', address)
        sys.exit(0)

    if subdomain is None:
        subdomain = platform.node().split(".")[0]

    fqdn = '%s.%s' % (subdomain, domain)
    logger.debug('FQDN is: %s', fqdn)
    upsert(fqdn, address, ttl, conf)


# noinspection PyUnusedLocal

def stub(client):
    pass


def upsert(fqdn, address, ttl, conf):

    change_batch = {
            'Comment': 'comment',
            'Changes': [
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': fqdn,
                        'Type': 'A',
                        'TTL': ttl,
                        'ResourceRecords': [
                            {
                                'Value': address
                            },
                        ],
                    }
                },
            ]
        }

    logger.debug(repr(change_batch))
    client = boto3.client('route53', aws_access_key_id=conf.aws_key,
                          aws_secret_access_key=conf.aws_sec_key)
    stub(client)

    response = client.change_resource_record_sets(
        HostedZoneId=conf.hosted_zone_id, ChangeBatch=change_batch)

    logger.info("DNS record status %s ", response['ChangeInfo']['Status'])
    logger.info("DNS record response code %s ", response['ResponseMetadata'][
        'HTTPStatusCode'])


def run(cf=None):
    if cf is None:
        cf = Conf()
    try:
        args = cli(cf)
        update(args.address, subdomain=args.subdomain, domain=args.domain,
               ttl=args.ttl, conf=cf, debug=args.debug)
    except (WrongPermissions, ClientError) as exc:
        logger.error(exc.args[0])
