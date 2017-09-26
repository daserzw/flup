
import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import flup
import ldap
import unittest
import tempfile

class FlupTestCase(unittest.TestCase):


    def setUp(self):
        self.app = flup.app.test_client()
        
    def tearDown(self):
        pass
        
    def test_index(self):
        rv = self.app.get('/')
        assert b'FLUP' in rv.data
    
    def test_login(self):
        rv = self.app.post('/', data=dict(username='mario', password='mariopw'))
        
    
        
if __name__ == '__main__':
    unittest.main()
