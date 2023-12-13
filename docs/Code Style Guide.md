# Code Style Guide

## Variable (Attribute), Function (Method), and Class Naming

Regular variables (attributes) and functions (methods) should be separated by underscores.

```python
def example_function(arg_a: int, arg_b: int) -> int:
    middle_var = arg_a + arg_b
    return middle_var
```

Constant variables should be fully capitalized.

```python
CONSTANT_ACCELERATION: float = -9.8
```

## Type Annotation

### Variables

Module or class level variables should be type-annotated.

```python
_line_separator: str = "\n"


class Animal(object):
    def __init__(self, arg_a: str):
        self.arg_a: str = arg_a + _line_separator
```

### Functions (Methods)

Every publicly exposed interface should be type-annotated.

```python
def example_function(arg_a: int, arg_b: int) -> int:
    return arg_a + arg_b
```

If it returns `None`, the annotation cannot be omitted.

```python
def example_function(arg_a: int, arg_b: int) -> None:
    print(arg_a, arg_b)
```

## Namespace Exposure

### Imports

Only imports from the same package should be in their original names. External imports should be given protected alias.

```python
from typing import Any as _Any
from sys import exit as _exit

from .example import something
```

### Attributes
