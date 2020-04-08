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

##### `HLVE303` -- `str()` is renamed to `bytes()` in Python 3. Use `six.text_type()` or `six.binary_type()` instead

**Example:**

```py
variable = str(123)
```

**Correct example:**

```py
from six import text_type

variable = text_type(123)
```

Most of the time you can safely replace `str()` with `six.text_type()`.

##### `HLVE309` -- Replace Python 2-only import `<module_name>` with `six.moves.<module_name>`

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

##### `HLVE311` -- Replace implicit relative import `<module_name>` with `.<module_name>`

Currently, only the following module names can be detected:

| Module name | Notes |
| --- | --- |
| ``forms`` | |
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
from models import MyModel

from serializers import MyModelSerializer
```

**Correct example:**

```py
from .models import MyModel

from .serializers import MyModelSerializer
```

##### `HLVE312` -- `<expected_content>` must be of type `six.binary_type` when it's compared to `<response_content>`

`TestClient` of Django returns `six.binary_type` both in Python 2 and Python 3.

Note that we are only supporting `assertIn` and `assertNotIn` unittest
assertions for now.

**Example:**

```py
from __future__ import unicode_literals

class MyTestCase(TestCase):

    def test_get(self):
        response = self.client.get('https://www.holvi.com')
        self.assertIn('foo', response.content)

    def test_get_404(self):
        response = self.client.get('https://www.holvi.com/404/')
        expected = 'bar'
        self.assertIn(expected, response.content)
```

**Correct example:**

```py
from __future__ import unicode_literals

class MyTestCase(TestCase):

    def test_get(self):
        response = self.client.get('https://www.holvi.com')
        self.assertIn(b'foo', response.content)

    def test_get_404(self):
        response = self.client.get('https://www.holvi.com/404/')
        expected = b'bar'
        self.assertIn(expected, response.content)
```

##### `HLVE313` -- `BaseException.message` has been removed in Python 3. Use `six.text_type(<exception_variable>)` instead

**Example:**

```py
try:
    1/0
except Exception as exc:
    assert 'integer division' in exc.message
```

**Correct example:**

```py
from six import text_type

try:
    1/0
except Exception as exc:
    assert 'integer division' in text_type(exc)
```

**Python 2 note:** An encoding must be specified if `exc` may contain non-ASCII
characters:

```py
from six import PY3
from six import text_type

try:
    1/0
except Exception as exc:
    if PY3:
        exc_message = text_type(exc)
    else:
        exc_messge = text_type(exc, 'utf-8')
    assert 'integer division' in exc_message
```

##### `HLVE314` -- `dict.<deprecated_method>` has been removed in Python 2. Use `six.<deprecated_method>` instead

Currently supported `dict` methods:

| Python 2 `dict` method | ``six`` replacement |
| --- | --- |
| ``dict.iterkeys`` | ``six.iterkeys`` |
| ``dict.itervalues`` | ``six.itervalues`` |
| ``dict.iteritems`` | ``six.iteritems`` |

**Example:**

```py
d = {}

for k, v in d.iteritems():
    print k, v
```

**Correct example:**

```py
from six import iteritems

d = {}

for k, v in iteritems(d):
    print k, v
```

#### Warnings

##### `HLVW301` -- First argument of `unicode()` may contain non-ASCII characters. We recommend passing encoding explicitly

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

##### `HLVE006` and `HLVE007` -- Do not use %-formatting or `str.format()` inside logging format strings

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

##### `HLVE009` -- `<str_format>` is used inside `<logging_call>` but no value is passed to it

**Example:**

```py
import logging

logging.debug('Foo: %s')
```

**Correct example:**

```py
import logging

logging.debug('Foo: %s', 'test')
```

##### `HLVE010` -- `logging.exception()` must be used inside an except block

**Example:**

```py
import logging

logging.exception('Something went wrong.')
```

**Correct example:**

```py
import logging

try:
    1/0
except Exception:
    logging.exception('Something went wrong.')
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

##### `HLVE013` -- Do not leave docstring in `<name>` empty

**Example:**

```py
def get_events(client):
    """"""
    return client.get_events(period=constants.TWO_MONTHS)
```

**Correct example:**

```py
def get_events(client):
    """Return list of event from third-party API."""
    return client.get_events(period=constants.TWO_MONTHS)

def get_events(client):
    return client.get_events(period=constants.TWO_MONTHS)
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

##### `HLVE015` -- `<old_name>` unittest assertion is deprecated. Use `<new_name>` instead

| Deprecated assertion name | Preferred assertion name |
| --- | --- |
| ``assertEquals`` | ``assertEqual`` |

##### `HLVE016` -- Use of `assert` statement can be dangerous. Raise `AssertionError` or proper exceptions instead

Quoting from the [official Python documentation](https://docs.python.org/2/tutorial/modules.html#compiled-python-files):

> When the Python interpreter is invoked with the -O flag, optimized code is
> generated and stored in .pyo files. The optimizer currently doesn’t help
> much; it only removes assert statements.

See [this issue](https://github.com/IdentityPython/pysaml2/issues/451) from
`pysaml2` for a real world example of such a problem.

**Example:**

```py
assert self.request.user.age <= 18
```

**Correct example:**

```py
if self.request.user.age <= 18:
    raise ValueError('User age must be 18 or more')
```
