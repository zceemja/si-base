# SI-Base python package

A basic python package that converts numerical strings with units to base units.

Examples:

```python
from sibase import Value, Unit

value = Value('3e5 nm/ps')  # 3e+08 m/s
# value is instance of float with value if 3e8
float_value = value.to('km/s')  # 300000.0
# shorthand method:
float_value = value @ 'km/s' 

# Converting with units:
float_value = Unit('km/s').convert(3e8)
# shorthand methods:
float_value = 3e8 @ Unit('km/s')
float_value = Unit('km/s') @ 3e8

# Operations
# Note that this only compares numerical values, not units
Value('50 km') > '1e6 mm'  # True
Value('50 km') < '1e8 mm'  # True
Value('50 /km') == '50 km^-1'  # True

Value('50 km') + '50 km'  # 1e5 m (returns Value object, keeps units from LHS)
Value('50 km') - '1e4 m'  # 4e4 m (returns Value object, keeps units from LHS)
Value('50 km') * '100 m'  # 5e6 m^2 (returns Value object, unit updated)
Value('1 km') / '50 m'  # 20 (returns Value object, this case unitless)
Value('1 km') / '50 s'  # 20 m/s (returns Value object, units updated)

# Invert operation returns string with original units
~Value('50 km')  # 50 km
Value('50 km').original()  # 50 km
# Reduces same unit and prefix values, useful for multiply/divide operations 
Value('17 ps/nm/km/km').original(simplify=True)  # 17 ps/nm/km^2
```

Superscripts are enabled by default

```python
from sibase import Value, Unit
Unit.USE_SUBSCRIPTS = False  # Disable superscripts for units
Value('300mm^2/ps')  # 3e+08 m²s⁻¹
```

Supports converting units with powers such as:

```python
from sibase import Value

Value('-21 ps^2/km')  #  -2.1e-26 s^2/m
Value('17 ps/nm/km')  #  1.7e-05 s/m^2

# dB, dBm and Np (Nepers) are special units
Value('20 dB/km')  # 0.1 /m 
Value('2.3 km/Np')  # ~10.05 m 
Value('-20 dB') @ 'dBm'  # 10.0
Value('0.2 dB/km') @ 'Np/m'  # -3.43

# More special units can be added
from sibase import set_special_unit

set_special_unit(
    'log',  # name of unit 
    lambda x, _math: _math.log(x),  # function to convert to SI base  
    lambda x, _math: _math.exp(x)   # inverse of above
)
Value('10 log') # 2.30258509 
Value('2.3') @ 'log' # ~10 
Value('1π')  # 3.14159265 ( π treated as special unit )

```

Numpy, probably could also applied for other libraries

```python
from sibase import to_base, Unit
import numpy as np

np_array = np.array([...])
# Convert from nonstandard:
si_array = to_base(np_array, 'km/s')

# Convert to other units
not_base_array = Unit('km/s').convert(si_array)
# shorthand method (will not work other way around for numpy arrays):
not_base_array = Unit('km/s') @ si_array
```