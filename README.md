# flake8-holvi

flake8-holvi is a flake8 plugin that helps writing Python 3-compatible and more
Pythonic code in Holvi projects.

## Installation and usage

If you are a Holvi employee, you can install it from our PyPI mirror:

```bash
$ pip install --index-url https://pypi.holvi.net/holvi/staging flake8-holvi
```

Or you can install it directly from GitHub:

```bash
$ pip install -e git+https://github.com/holvi/flake8-holvi.git#egg=flake8-holvi
```

You don't need to do anything else to be able to use it. However, you can use the
`--select` option if you only want to see violations found by flake8-holvi:

```bash
$ flake8 --select=HLV bankgw/
```

Or in `setup.cfg`, you can use the `enable-extensions` setting:

```ini
[flake8]
enable-extensions=HLV
```

Reporting warnings can be disabled by passing the `--disable-warnings` option.

## Checks

Currently, flake8-holvi detects the following cases as errors and warnings
respectively:

### Python 3

#### Errors

##### `HLVE301` -- Import `print_function` from `__future__` and use `print()`

**Example:**

```py
print 'spam'
```

**Correct example:**

```py
from __future__ import print_function

print('spam')
```

##### `HLVE302` -- `unicode()` is renamed to `str()` in Python 3. Use `six.text_type()` instead

**Example:**

```py
variable = unicode('spam eggs')
```

**Correct example:**

```py
from six import text_type

variable = text_type('spam eggs')
```

##### `HLVE303` -- `str()` is renamed to `bytes()` in Python 3. Use `six.binary_type()` instead

**Example:**

```py
variable = str(u'spam eggs')
```

**Correct example:**

```py
from six import binary_type

variable = binary_type(u'spam eggs')
```

##### `HLVE309` -- Replace Python 2-only import `<module_name>` with `six.moves.<module_name>`.

Full list of `six.moves` can be found at https://six.readthedocs.io/#module-six.moves

**Example:**

```py
import urlparse

import ConfigParser
```

**Correct example:**

```py
from six.moves.urllib import parse

from six.moves import configparser
```

##### `HLVE310` -- Replace Python 2-only unittest assertion `<name>` with `six.<name>`

Currently supported unittest assertions:

| Python 2 assertion | ``six`` replacement |
| --- | --- |
| ``assertItemsEqual`` | ``six.assertCountEqual`` |
| ``assertRaisesRegexp`` | ``six.assertRaisesRegex`` |
| ``assertRegexpMatches`` | ``six.assertRegex`` |

##### `HLVE311` -- Replace implicit relative import `<module_name>` with `.<module_name>`.

Currently, only the following module names can be detected:

| Module name | Notes |
| --- | --- |
| ``exceptions`` | |
| ``models`` | |
| ``serializers`` | |
| ``signals`` | |
| ``tasks`` | |
| ``views`` | |
| ``api`` | Holvi-specific module |
| ``constants`` | Holvi-specific module |
| ``providers`` | Holvi-specific module |

**Example:**

```py
from model import MyModel

from serializer import MyModelSerializer
```

**Correct example:**

```py
from .model import MyModel

from .serializer import MyModelSerializer
```

#### Warnings

##### `HLVW301` -- First argument of `unicode()` may contain non-ASCII characters. We recommend passing encoding explicitly.

In Python 2, the default string encoding is `'ascii'`. As a result of this,
if you call `unicode()` without specifying an encoding, it may raise
`UnicodeDecodeError` depending on the string you've passed to `unicode()`.

**Example:**

```py
>>> unicode('text with non-ASCII characters: ıçğüş')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
UnicodeDecodeError: 'ascii' codec can't decode byte 0xc4 in position 32: ordinal not in range(128)
>>> content = get_data_from_external_api()
# This call may fail if 'content' contains non-ASCII characters.
>>> unicode(content)
Traceback (most recent call last):
  File "<stdin>", line 3, in <module>
UnicodeDecodeError: 'ascii' codec can't decode byte 0xc4 in position 32: ordinal not in range(128)
```

**Correct example:**

```py
>>> unicode('text with non-ASCII characters: ıçğüş', 'utf-8')
u'text with non-ASCII characters: \u0131\xe7\u011f\xfc\u015f'
>>> content = get_data_from_external_api()
>>> unicode(content, 'utf-8')
u'text with non-ASCII characters: \u0131\xe7\u011f\xfc\u015f'
```

### Common programming mistakes

#### Errors

##### `HLVE006` and `HLVE006` -- Do not use %-formatting or `str.format()` inside logging format strings

The string interpolation operation should be deferred to the `logging`
module for the following reasons:

* The string interpolation is performed even if logging is disabled in the
  following example:
  
  ```py
  logger.debug('Something bad happened: %s' % user.id)
  ```
  
  This could cause performance issues especially if `user` information
  can be fetched from an external service such as a third-party API or
  database.
  
  This pattern can also call `str()`, `unicode()` or `repr()` functions
  implicitly.
  
* It can limit the ability of customizing behavior of the `logging`
  module. It's advised to pass raw data to `logging.Handler`,
  `logging.Formatter` and `logging.Filter` classes.

**Examples:**

```py
logger.debug('Some debug information: %s' % foo)

logger.debug('Some debug information: {}'.format(foo))
```

**Correct examples:**

```py
logger.debug('Some debug information: %s', foo)
```

##### `HLVE008` -- `<name>` must be passed to the lambda to avoid late binding issue in Python

You can check out the following links to learn more about this problem:

* https://medium.com/@adriennedomingus/debugging-background-tasks-inside-loops-and-transactions-cd1230d6280d
* https://docs.python-guide.org/writing/gotchas/#late-binding-closures

**Example:**

```py
for event in events:
    transaction.on_commit(lambda: task.apply_async((event.id,)))
```

**Correct example:**

```py
for event in events:
    transaction.on_commit(lambda event=event: task.apply_async((event.id,)))
```

##### `HLVE012` -- `<name>` cannot be found in `lambda`'s default argument(s)

**Example:**

```py
for event in events:
    transaction.on_commit(lambda user=user: task.apply_async((event.id, user.email)))
```

**Correct example:**

```py
for event in events:
    transaction.on_commit(lambda event=event, user=user: task.apply_async((event.id, user.email)))
```

##### `HLVE014` -- Invoking `<assertion_name>` directly is unnecessary. Use `assertEqual` instead

The `assertEqual` method will call the following unittest assertions implicitly:

* `assertMultiLineEqual`
* `assertSequenceEqual`
* `assertListEqual`
* `assertTupleEqual`
* `assertSetEqual`
* `assertDictEqual`

More information can be found at https://docs.python.org/2/library/unittest.html#unittest.TestCase.addTypeEqualityFunc

**Example:**

```py
self.assertListEqual(expected, got)
```

**Correct example:**

```py
self.assertEqual(expected, got)
```
