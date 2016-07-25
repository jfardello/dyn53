import unittest
from . import test_cli, test_client


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTests(unittest.makeSuite(test_cli.TestCli))
    test_suite.addTests(unittest.makeSuite(test_client.TestClient))
    return test_suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
