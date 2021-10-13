# SI-Base python package

A basic python package that converts numerical strings with units to base units.

Examples:

```python
from sibase import Unit

value = Unit('3e5 nm/ps')  #  3e+08 m/s
# value is instance of float with value if 3e8
float_value = value.to('km/s')  # 300000.0
```

Supports converting units with powers such as:

```python
Unit('-21 ps^2/km')  #  -2.1e-26 s^2/m
Unit('17 ps/nm/km')  #  1.7e-05 s/m^2
```