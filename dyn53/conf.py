import os
import stat
import logging
import configparser
import platform
from argparse import ArgumentParser


class WrongPermissions(Exception):
    pass

DEFAULTS = {'domain': 'domain.tld.',
            'ttl': 300,
            'debug': False,
            'hosted_zone_id': "My hosted Zone Id",
            'aws_key': "MY KEY",
            'aws_sec_key': "MY SECRET KEY"}

CONF_FILE = "~/.config/dyn53.conf"


class Conf:
    aws_key = None
    aws_sec_key = None
    domain = None
    debug = None
    ttl = None
    hosted_zone_id = None

    def __init__(self, defaults=DEFAULTS, conf_file=CONF_FILE):
        conf_file = os.path.expanduser(conf_file)
        self.log = logging.getLogger('dyn53')
        self.log.debug("Using conf_file = %s", conf_file)
        self.conf = configparser.ConfigParser()
        self.conf['dyn53'] = defaults
        if os.path.exists(conf_file):
            self.conf.read(conf_file)
            group_read = bool(os.stat(conf_file).st_mode & stat.S_IROTH)
            other_read = bool(os.stat(conf_file).st_mode & stat.S_IROTH)
            owner_read = not bool(os.stat(conf_file).st_mode & stat.S_IRUSR)
            if group_read or other_read or owner_read:
                raise WrongPermissions("%s should be readable only by the "
                                       "effective owner." % conf_file)
        else:
            sample_file = "%s.sample" % conf_file
            self.log.info("Creating sample config file: %s", sample_file)
            with open(sample_file, 'w') as fp:
                self.log.debug("Creating %s", sample_file)
                self.conf.write(fp)
            os.chmod(sample_file, 0o600)
            raise SystemExit("No config file found, exiting.")

        self.__dict__.update(self.conf["dyn53"])
        self.__dict__.update({"debug": self.conf["dyn53"].getboolean(
            "debug")})
        self.__dict__.update({"ttl": self.conf["dyn53"].getint(
            "ttl")})


def cli(cf):
    subdomain = platform.node().split(".")[0]
    parser = ArgumentParser(description='route53 dynamic IP address updater')
    parser.add_argument('-a', '--address', help='force this address.',
                        default=None)
    parser.add_argument('-d', '--domain', default=cf.domain,
                        help='Use this domain. Defaults to "%s")' % cf.domain)
    parser.add_argument('-s', '--subdomain', default=subdomain,
                        help='Subdomain, Defaults to "%s."' % subdomain)
    parser.add_argument('-t', '--ttl', default=cf.ttl, type=int,
                        help='Time to live (TTL), defaults to "%s."' % cf.ttl)
    parser.add_argument('-D', '--debug', default=cf.debug, action='store_true',
                        help="Enable debug messages")
    return parser.parse_args()
