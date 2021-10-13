import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from sibase import Unit


class TestConvert(unittest.TestCase):

    def test_unit0(self):
        val = Unit('3e5 nm/ps')
        self.assertEqual(3e8, val)
        self.assertEqual('m/s', val.units)
        self.assertEqual(3e5, val.to('nm/ps'))
        self.assertEqual(3e5, val.to('nm ps^-1'))

    def test_unit1(self):
        val = Unit('-21 ps^2/km')
        self.assertEqual(-2.1e-26, val)
        self.assertEqual('s^2/m', val.units)
        self.assertEqual(-21, val.to('ps^2/km'))
        self.assertEqual(-21, val.to('ps^2 km^-1'))

    def test_unit2(self):
        val = Unit('17 ps/nm/km')
        self.assertEqual(1.7e-05, val)
        self.assertEqual('s/m^2', val.units)
        self.assertEqual(17, val.to('ps/nm/km'))
        self.assertEqual(17, val.to('ps nm^-1 km^-1'))


if __name__ == '__main__':
    unittest.main()
