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

_si_unit_re = re.compile(r'^(-?[0-9]+(\.[0-9]+)?(e[-+]?[0-9]+)?)(.*)$')
_si_prefix_re = re.compile(
    r'([ /*∙]?)' +                                      # divider
    rf'([{"".join(_si_prefix.keys())}]?)' +             # prefix
    r'([^\^/*⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻ ]*)' +                        # unit
    r'(\^[\-]?[0-9]+(\.[0-9]+)?|[⁺⁻]?[⁰¹²³⁴⁵⁶⁷⁸⁹]+)?'   # power_str
)

_superscripts = "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻"
_superscripts_re = re.compile(r'^[⁺⁻]?[⁰¹²³⁴⁵⁶⁷⁸⁹]+$')


def _num_to_superscript(value: int) -> str:
    try:
        digits = ''.join([_superscripts[int(digit)] for digit in str(value).lstrip('-')])
        if value < 0:
            digits = _superscripts[-1] + digits
        return digits
    except ValueError:
        return str(value).rstrip('0').rstrip('.')


def _superscript_to_num(value: str) -> float:
    if _superscripts_re.match(value) is not None:
        digits = ''.join([str(_superscripts.find(digit)) for digit in value.lstrip(_superscripts[-2:])])
        if value.startswith(_superscripts[-1]):
            digits = "-" + digits
        return float(digits)
    else:
        return float(value)


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


def float_repr(value: float) -> str:
    """ Pretty print float """
    spl = '{:e}'.format(value).split('e')
    exp = 'e' + spl[1]
    if abs(int(spl[1][-2:])) <= 3:
        spl[0] = '{:.8f}'.format(value)
        exp = ''
    return spl[0].rstrip('0').rstrip('.') + exp


class Unit:
    USE_SUBSCRIPTS = True
    USE_DOT_OPERATOR = True

    def __init__(self, string):
        self.units = OrderedDict()
        self.scale = 0
        self.modifiers = []
        self.original = []

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
            power_str = power_str.lstrip('^')
            power = _superscript_to_num(power_str) if len(power_str) > 0 else 1
            if divider == '/':
                power = -power
            self.scale += _si_prefix[prefix] * power
            if unit in self.units:
                self.units[unit] += power
            else:
                self.units[unit] = power
            self.original.append((unit, prefix, power))

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

    def _repr_unit(self, unit, power, superscript) -> str:
        result = ''
        if superscript and float(power).is_integer():
            result += unit
            if power != 1:
                result += _num_to_superscript(int(power))
        else:
            if power < 0:
                result += '/'
            result += unit
            if abs(power) > 1:
                result += ('^%f' % abs(power)).rstrip('0').rstrip('.')
        return result

    def str(self, original=False, superscript=None, dot_operator=None, simplify=False):
        """
        Prints units as string
        :param original: print units in initial form
        :param superscript: print using superscripts
        :param dot_operator: use dot for unit separation
        :param simplify: marge units with same prefix
        :return: unit string
        """
        if superscript is None:
            superscript = self.USE_SUBSCRIPTS
        if dot_operator is None:
            dot_operator = self.USE_DOT_OPERATOR
        result = []
        if original:
            _original = self.original
            if simplify:
                concated = list(map(lambda x: (x[1] + x[0], x[2]), self.original))
                used = set()
                _original = []
                for i, (unit, power) in enumerate(concated):
                    if unit in used:
                        continue
                    power += sum([p for u, p in concated[i+1:] if unit == u])
                    if power != 0:
                        _original.append((unit, '', power))
                    used.add(unit)
            for unit, prefix, power in _original:
                result.append(self._repr_unit(prefix + unit, power, superscript))
        else:
            for unit, power in self.units.items():
                result.append(self._repr_unit(unit, power, superscript))
        if superscript and dot_operator:
            return '∙'.join(result)
        return ''.join([res if res.startswith('/') else ' ' + res for res in result]).strip()

    def __repr__(self):
        return self.str()

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
        other_original = other.original
        if subtract:
            other_original = [(unit, prefix, -power) for unit, prefix, power in other_original]
        new_inst.original = self.original + other_original
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
                units = _units or ''
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

    def original(self, **kwargs):
        """
        returns value with original units that it as initialised with
        """
        value = self.__units__.convert(self)
        return f'{float_repr(value)} {self.__units__.str(original=True, **kwargs)}'

    def __invert__(self):
        return self.original()

    def to(self, unit):
        """
        Converts SI unit to provided units,
        i.e. Unit('3e8 m/s').to('nm/ps') == 3e5
        :param unit: string of unit to convert to
        :return: value as a float
        """
        return Unit(unit).convert(self)

    def __repr__(self):
        val = float_repr(self)
        return f'{val} {self.__units__}'

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
