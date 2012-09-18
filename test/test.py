import unittest
import cork

class PseudorandomTest(unittest.TestCase):
    def testSeed(self):
        prnd = cork.Pseudorandom(555)
        control_value = prnd.random()
        
        prnd.seed()
        prnd.seed("*args", 2, {"key": 90210}, ['foo', 187])
        prnd.seed({})
        prnd.seed(555)
        
        self.failUnless(prnd.random() == control_value)
