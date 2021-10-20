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
```

Supports converting units with powers such as:

```python
from sibase import Value

Value('-21 ps^2/km')  #  -2.1e-26 s^2/m
Value('17 ps/nm/km')  #  1.7e-05 s/m^2
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