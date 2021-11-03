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

_special_units = {
    'dB': None
}

_si_unit_re = re.compile(r'^(-?[0-9]+(\.[0-9]+)?(e-?[0-9]+)?)([/^.* \-\w]+)$')
_si_prefix_re = re.compile(rf'([ /*]?)([{"".join(_si_prefix.keys())}]?)([^\^/* ]*)(\^[\-]?[0-9]+(\.[0-9]+)?)?')


def _parse_number(string):
    m0 = _si_unit_re.match(string)
    if m0 is None:
        raise ValueError("Failed to get value and units")
    value_str, _, _, units = m0.groups()
    return value_str, units


def to_base(value, units=''):
    if isinstance(value, str):
        value_str, _units = _parse_number(value)
        value = float(value_str)
        if units != '':
            units = _units
    elif not hasattr(value, '__mul__') or not hasattr(value, '__pow__'):
        raise ValueError(f"Invalid value type '{value.__class__.__name__}'")
    m = Unit(units)
    for mod in m.modifiers:
        value = mod(value)
    return value * 10 ** m.scale


class Unit:
    def __init__(self, string):
        self.units = OrderedDict()
        self.scale = 0
        self.modifiers = []

        for divider, prefix, unit, power_str, _ in _si_prefix_re.findall(string)[:-1]:
            unit_group = prefix + unit
            if unit_group in _special_units:
                if power_str != '':
                    raise ValueError(f'Power for special unit {unit_group + power_str} is not supported')
                func = _special_units[unit_group]
                if func is not None:
                    self.modifiers.append(func if divider == '/' else lambda x: 1 / func(x))
                continue
            if unit == '':
                unit = prefix
                prefix = ''
            power = float(power_str[1:]) if len(power_str) > 1 else 1
            if divider == '/':
                power = -power
            self.scale += _si_prefix[prefix] * power
            if unit in self.units:
                self.units[unit] += power
            else:
                self.units[unit] = power

    def convert(self, value):
        """
        :param value: some number in standard from
        :return: converted value
        """
        if len(self.modifiers) > 0:
            raise ValueError("Special units are not implemented to be converted")
        if not hasattr(value, '__mul__') or not hasattr(value, '__pow__'):
            raise ValueError(f"Invalid value type '{value.__class__.__name__}'")
        return value * 10 ** -self.scale

    def __rmatmul__(self, left):
        """
        shorthand for to function, works as: some_float @ Unit('nm/ps')
        """
        return self.convert(left)

    def __matmul__(self, right):
        """
        shorthand for to function, works as: Unit('nm/ps') @ some_float
        """
        return self.convert(right)

    def __repr__(self):
        result = ''
        for unit, power in self.units.items():
            if power < 0:
                result += '/'
            result += unit
            if abs(power) > 1:
                result += ('^%f' % abs(power)).rstrip('0').rstrip('.')
        return result

    def _add(self, other, subtract=False):
        """ Merge add from other unit object """
        new_inst = Unit('')
        if isinstance(other, str):
            other = Unit(other)
        for unit in self.units.keys() - other.units.keys():
            new_inst.units[unit] = self.units[unit]
        for unit in other.units.keys() - self.units.keys():
            new_inst.units[unit] = -other.units[unit] if subtract else other.units[unit]
        for unit in self.units.keys() & other.units.keys():
            new_inst.units[unit] = self.units[unit]
            if unit not in other.units:
                continue
            new_inst.units[unit] += -other.units[unit] if subtract else other.units[unit]
            if new_inst.units[unit] == 0:
                del new_inst.units[unit]
        # Sort by power then by alphabet of unit name
        new_inst.units = OrderedDict(sorted(new_inst.units.items(), key=lambda x: (-x[1], x[0])))
        return new_inst

    def _sub(self, other):
        """ Merge subtract from other unit object """
        return self._add(other, subtract=True)


class Value(float):
    def __new__(cls, value, units=''):
        if isinstance(value, str):
            value_str, _units = _parse_number(value)
            value = float(value_str)
            if units == '':
                units = _units
        if not isinstance(units, Unit):
            units = Unit(units)
        for mod in units.modifiers:
            value = mod(value)
        _value = value * 10 ** units.scale
        instance = super().__new__(cls, _value)
        instance.__units__ = units
        return instance

    @property
    def units(self):
        """ Returns si units as a string """
        return str(self.__units__)

    def __matmul__(self, unit):
        """
        shorthand for to function, works as Unit('3e8 m/s') @ 'nm/ps'
        """
        return self.to(unit)

    def to(self, unit):
        """
        Converts SI unit to provided units,
        i.e. Unit('3e8 m/s').to('nm/ps') == 3e5
        :param unit: string of unit to convert to
        :return: value as a float
        """
        return Unit(unit).convert(self)

    def __repr__(self):
        spl = '{:e}'.format(self).split('e')
        exp = 'e' + spl[1]
        if abs(int(spl[1][-2:])) <= 3:
            spl[0] = '{:.6f}'.format(self)
            exp = ''
        val = spl[0].rstrip('0').rstrip('.')
        return f'{val}{exp} {self.__units__}'

    def __eq__(self, x):
        if isinstance(x, str):
            x = Value(x)
        return super().__eq__(x)

    def __ne__(self, x):
        if isinstance(x, str):
            x = Value(x)
        return super().__ne__(x)

    def __gt__(self, x):
        if isinstance(x, str):
            x = Value(x)
        return super().__gt__(x)

    def __lt__(self, x):
        if isinstance(x, str):
            x = Value(x)
        return super().__lt__(x)

    def __ge__(self, x):
        if isinstance(x, str):
            x = Value(x)
        return super().__ge__(x)

    def __le__(self, x):
        if isinstance(x, str):
            x = Value(x)
        return super().__le__(x)

    def __sub__(self, x):
        if isinstance(x, str):
            x = Value(x)
        return Value(super().__sub__(x), self.units)

    def __add__(self, x):
        if isinstance(x, str):
            x = Value(x)
        return Value(super().__add__(x), self.units)

    def __mul__(self, x):
        if isinstance(x, str):
            x = Value(x)
            return Value(super().__mul__(x), self.__units__._add(x.__units__))
        return super().__mul__(x)

    def __truediv__(self, x):
        if isinstance(x, str):
            x = Value(x)
            return Value(super().__truediv__(x), self.__units__._sub(x.__units__))
        return super().__truediv__(x)

    def __floordiv__(self, x):
        if isinstance(x, str):
            x = Value(x)
            return Value(super().__floordiv__(x), self.__units__._sub(x.__units__))
        return super().__floordiv__(x)
