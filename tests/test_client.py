import os
import sys
import unittest
import platform
from datetime import datetime
from unittest.mock import patch, Mock, MagicMock

import certifi
from botocore.stub import Stubber

from dyn53 import dyn53
from dyn53 import conf

# make pycharm happy.
patch.object = patch.object

TEST_CONFIG = "/tmp/dyn53_test_%s" % os.getpid()

expected = {
    'HostedZoneId': 'My hosted Zone Id',
    'ChangeBatch': {
        'Comment': 'comment',
        'Changes': [{
            'Action': 'UPSERT',
            'ResourceRecordSet': {
                'TTL': 300,
                'ResourceRecords': [{'Value': '2.2.2.2'}],
                'Name': '%s.domain.tld.' % platform.node().split(".")[0],
                'Type': 'A'}
        }]
    }
}

response = {
    'ChangeInfo': {
        'Id': 'string',
        'Status': 'PENDING',
        'SubmittedAt': datetime(2016, 1, 1),
        'Comment': 'string'
    },
    'ResponseMetadata': {'HTTPStatusCode': 200}
}


def stub(client):

    stubber = Stubber(client)
    stubber.add_response('change_resource_record_sets', response, expected)
    stubber.activate()


class TestClient(unittest.TestCase):

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(TEST_CONFIG):
            os.remove(TEST_CONFIG)

    @patch('requests.get')
    def test_01_get_public_ip(self, mocked):
        address = dyn53.get_public_ip()
        mocked.assert_called_with(
            "https://api.ipify.org", verify=certifi.where())
        self.assertIsInstance(address, Mock)

    @patch('dns.resolver.query')
    @patch('dyn53.dyn53.get_public_ip')
    @patch('dyn53.dyn53.stub', new=stub)
    @patch('dyn53.dyn53.check', new=lambda x, y, z: False)
    def test_02_run(self, mock_get_public_ip, mock_query):
        mm1 = MagicMock()
        mm1.to_text.return_value = "1.1.1.1"
        mock_query.side_effect = [[mm1]]
        mock_get_public_ip.return_value = "2.2.2.2"
        with patch.object(sys, 'argv', ["dyn53", ]):
            dyn53.run(conf.Conf(conf_file=TEST_CONFIG))
