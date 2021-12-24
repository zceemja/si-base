import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sibase import Value, Unit


class TestConvert(unittest.TestCase):

    def test_unit0(self):
        val = Value('3e5 nm/ps')
        self.assertEqual(3e8, val)
        Unit.USE_SUBSCRIPTS = False
        self.assertEqual('m/s', val.units)
        self.assertEqual(3e5, val.to('nm/ps'))
        self.assertEqual(3e5, val @ 'nm/ps')
        self.assertEqual(3e5, val.to('nm ps^-1'))
        self.assertEqual(3e5, val @ 'nm ps^-1')
        self.assertEqual(3e5, 3e8 @ Unit('nm/ps'))

    def test_unit1(self):
        val = Value('-21 ps^2/km')
        self.assertEqual(-2.1e-26, val)
        Unit.USE_SUBSCRIPTS = False
        self.assertEqual('s^2/m', val.units)
        self.assertEqual(-21, val.to('ps^2/km'))
        self.assertEqual(-21, val @ 'ps^2/km')
        self.assertEqual(-21, val.to('ps^2 km^-1'))
        self.assertEqual(-21, val @ 'ps^2 km^-1')
        self.assertEqual(-21, -2.1e-26 @ Unit('ps^2 km^-1'))

    def test_unit2(self):
        val = Value('17 ps/nm/km')
        self.assertEqual(1.7e-05, val)
        Unit.USE_SUBSCRIPTS = False
        self.assertEqual('s/m^2', val.units)
        self.assertEqual(17, val.to('ps/nm/km'))
        self.assertEqual(17, val @ 'ps/nm/km')
        self.assertEqual(17, val.to('ps nm^-1 km^-1'))
        self.assertEqual(17, val @ 'ps nm^-1 km^-1')
        self.assertEqual(17, 1.7e-05 @ Unit('ps nm^-1 km^-1'))

    def test_unit3(self):
        val = Value('50 km^-1')
        Unit.USE_SUBSCRIPTS = False
        self.assertEqual(val == '50 /km', True)

    def test_unit4(self):
        val = Value('50 km')
        Unit.USE_SUBSCRIPTS = False
        self.assertEqual(val > '100 m', True)
        self.assertEqual(val < '5 Mm', True)
        self.assertEqual(val + '50 km', 100e3)
        self.assertEqual(val + '50 km', 100e3)
        self.assertEqual(val > '1e6 mm', True)
        self.assertEqual(val < '1e8 mm', True)
        self.assertEqual(Value('50 /km') == '50 km^-1', True)

        self.assertEqual(Value('50 km') + '50 km', 1e5)
        self.assertEqual(Value('50 km') - '1e4 m', 4e4)
        self.assertEqual(Value('50 km') * '100 m', 5e6)
        self.assertEqual((Value('50 km') * '100 m').units, 'm^2')
        self.assertEqual((Value('50 km') * '100 s').units, 'm s')
        self.assertEqual(Value('1 km') / '50 m', 20)
        self.assertEqual((Value('1 km') / '50 m').units, '')
        self.assertEqual(Value('1 km') / '50 s', 20)
        self.assertEqual((Value('1 km') / '50 s').units, 'm/s')
        self.assertEqual((Value('1 km') / '50 s' / '3s').units, 'm/s^2')

    def test_unit5(self):
        Unit.USE_SUBSCRIPTS = False
        self.assertEqual(Value('50 km').original(), '50 km')
        self.assertEqual(Value('17 ps/nm/km').original(), '17 ps/nm/km')
        self.assertEqual((Value('17 ps/nm/km') * '1 km').original(simplify=True), '17e-08 ps/nm')
        self.assertEqual((Value('17 ps/nm/km') / '1 km').original(simplify=True), '17 ps/nm/km^2')
        self.assertEqual((Value('17 ps/nm/km') * '1 km').original(simplify=False), '17 ps/nm/km km')
        self.assertEqual((Value('17 ps/nm/km') / '1 km').original(simplify=False), '17e-08 ps/nm/km/km')

        Unit.USE_DOT_OPERATOR = True
        self.assertEqual(Value('50 km').original(True), '50 km')
        self.assertEqual(Value('17 ps/nm/km').original(True), '17 ps∙nm⁻¹∙km⁻¹')


if __name__ == '__main__':
    unittest.main()
