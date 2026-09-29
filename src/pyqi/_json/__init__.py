"""
*`@module`* `_json/__init__.py`
"""
from .types import *
from ._serial import *
from . import (read, load, write)
from .read import (
    file as read_file, 
    object as read_object, 
    array as read_array, 
    scalar as read_scalar
)
from .load import (
    sequence as load_sequence,
    object as load_object,
    array as load_array,
    scalar as load_scalar
)
from .write import (
    file as write_file,
    dumpstr as to_str,
)