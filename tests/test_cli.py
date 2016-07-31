import os
import unittest
from unittest.mock import patch
from dyn53 import conf
import sys


TEST_CONFIG = "/tmp/dyn53_test_%s" % os.getpid()


def bad_perms():
    os.chmod(TEST_CONFIG, 0o644)


def move():
    os.rename("%s.sample" % TEST_CONFIG, TEST_CONFIG)


def fix_perms():
    os.chmod(TEST_CONFIG, 0o600)


class TestCli(unittest.TestCase):

    def test_01_create(self):
        with patch.object(sys, 'argv', ['dyn53', "-a", "200.1.1.1"]):
            with self.assertRaises(SystemExit):
                conf.Conf(conf_file=TEST_CONFIG)
        self.assertTrue(os.path.exists("%s.sample" % TEST_CONFIG))

    def test_03_read_conf(self):
        move()
        with patch.object(sys, 'argv', ['dyn53', "-a", "200.1.1.1"]):
            cf = conf.Conf(conf_file=TEST_CONFIG)
        self.assertEqual(cf.ttl, 300)
        self.assertEqual(cf.debug, False)

    def test_04_wrong_perm(self):
        bad_perms()
        with patch.object(sys, 'argv', ['dyn53', "-a", "200.1.1.1"]):
            with self.assertRaises(conf.WrongPermissions):
                conf.Conf(conf_file=TEST_CONFIG)

    def test_05_args(self):
        fix_perms()
        args = "dyn53 -a 200.0.0.1 -d foo.tld -s box -t 300".split()
        with patch.object(sys, 'argv', args):
            mocked = conf.cli(conf.Conf(conf_file=TEST_CONFIG))
        self.assertEqual(mocked.address, "200.0.0.1")
        self.assertEqual(mocked.domain, "foo.tld")
        self.assertEqual(mocked.subdomain, "box")
        self.assertEqual(mocked.ttl, 300)
        self.assertEqual(mocked.debug, False)
