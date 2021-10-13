import re
from collections import OrderedDict

_si_prefix = {
    'Y': 24,
    'Z': 21,
    'E': 18,
    'P': 15,
    'T': 12,
    'G': 9,
    'M': 6,
    'k': 3,
    'h': 2,
    '': 0,
    # 'da': 1e1,
    'd': -1,
    'c': -2,
    'm': -3,
    'u': -6,
    'µ': -6,
    'n': -9,
    'p': -12,
    'f': -15,
    'a': -18,
    'z': -21,
    'y': -24,
}

_si_unit_re = re.compile(r'^(-?[0-9]+(\.[0-9]+)?(e-?[0-9]+)?)([/^.* \w]+)$')
_si_prefix_re = re.compile(rf'([ /*]?)([{"".join(_si_prefix.keys())}]?)([^\^/* ]*)(\^[\-]?[0-9]+(\.[0-9]+)?)?')


def _parse_units(string):
    si_units = OrderedDict()
    scale = 0
    for divider, prefix, unit, power_str, _ in _si_prefix_re.findall(string)[:-1]:
        if unit == '':
            unit = prefix
            prefix = ''
        power = float(power_str[1:]) if len(power_str) > 1 else 1
        if divider == '/':
            power = -power
        scale += _si_prefix[prefix] * power
        if unit in si_units:
            si_units[unit] += power
        else:
            si_units[unit] = power
    return scale, si_units


def _parse_number(string):
    m0 = _si_unit_re.match(string)
    if m0 is None:
        raise ValueError("Failed to get value and units")
    value_str, _, _, units = m0.groups()
    return value_str, units


class Unit(float):
    def __new__(cls, value, units=None):
        value_str, _units = _parse_number(value)
        if units is not None:
            _units = units
        scale, si_units = _parse_units(_units)
        _value = float(value_str) * 10 ** scale
        instance = super().__new__(cls, _value)
        instance.__units__ = si_units
        return instance

    @property
    def units(self):
        """ Returns si units as a string """
        result = ''
        for unit, power in self.__units__.items():
            if power < 0:
                result += '/'
            result += unit
            if abs(power) > 1:
                result += ('^%f' % abs(power)).rstrip('0').rstrip('.')
        return result

    def to(self, unit):
        """
        Converts SI unit to provided units,
        i.e. Unit('3e8 m/s').to('nm/ps') == 3e5
        :param unit: string of unit to convert to
        :return: value as a float
        """
        scale, _ = _parse_units(unit)
        return self * 10 ** -scale

    def __repr__(self):
        spl = '{:e}'.format(self).split('e')
        val = spl[0].rstrip('0').rstrip('.')
        if spl[1][-2:] != '00':
            val += 'e' + spl[1]
        return val + ' ' + self.units

