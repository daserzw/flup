import os
import flup
import unittest
import tempfile

class FlupTestCase(unittest.TestCase):

    def setUp(self):
        self.app = flup.app.test_client()

    def tearDown(self):
        # TODO
        pass
        
    def test_index(self):
        rv = self.app.get('/')
        assert b'Flask Ldap User Password changer' in rv.data
        
if __name__ == '__main__':
    unittest.main()
