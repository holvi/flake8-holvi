# flake8-holvi

flake8-holvi is a flake8 plugin that helps writing Python 3-compatible and more
Pythonic code in Holvi projects.

## Installation and usage

It's not uploaded to our PyPI server yet. The simplest way to install it is from
GitHub with pip:

```bash
$ pip install -e git+https://github.com/holviberker/flake8-holvi.git#egg=flake8-holvi
```

You don't need to do anything else to be able to use it. However, you can use the
`--select` option if you only want to see violations found by flake8-holvi:

```bash
$ flake8 --select=HLV bankgw/
```

## Checks

Currently, flake8-holvi detects the following cases as errors and warnings
respectively:

### Errors

1. ```py
   unicode(...)  # Should be replaced with six.text_type().
   ```

2. ```py
   # Should have encoding parameter.
   unicode('text with non-ASCII characters: ıçğüş')
   ```

   Correct usage:

   ```py
   unicode('text with non-ASCII characters: ıçğüş', 'utf-8')
   ```

3. ```py
   # Should be used a non-ASCII encoding.
   unicode('text with non-ASCII characters: ıçğüş', 'ascii')
   ```

   Correct usage:

   ```py
   unicode('text with non-ASCII characters: ıçğüş', 'utf-8')
   ```

4. Incorrect usage:

   ```py
   logger.debug('Some debug information: %s' % foo)
   ```

   Correct usage:

   ```py
   logger.debug('Some debug information: %s', foo)
   ```

5. Incorrect usage:

   ```py
   logger.debug('Some debug information: {}'.format(foo))
   ```

   Correct usage:

   ```py
   logger.debug('Some debug information: %s', foo)
   ```

6. ```py
   str(...)  # Should be replaced with six.binary_type().
   ```

### Warnings

1. Potentially dangerous usage:

   ```py
   ascii_only_content = get_data_from_external_api()
   unicode(ascii_only_content)
   ```

   Safer usage since the default string encoding is `'ascii'` in
   Python 2 and `get_data_from_external_api()` can return non-ASCII
   data:

   ```py
   unicode(ascii_only_content, 'utf-8')
   ```

2. Potentially dangerous usage:

   ```py
   ascii_only_content = get_data_from_external_api()
   unicode(ascii_only_content, 'ascii')
   ```

   `'ascii'` should be passed only if we are 100% sure `ascii_only_content`
   will always be ASCII-only:

   ```py
   >>> non_ascii_content = "ıçğü"
   >>> unicode(non_ascii_content)
   Traceback (most recent call last):
     File "<stdin>", line 1, in <module>
   UnicodeDecodeError: 'ascii' codec can't decode byte 0xc4 in position 0: ordinal not in range(128)
   ```

   Otherwise use a more appropriate encoding:

   ```py
   unicode(ascii_only_content, better_encoding)
   ```

## Possible future improvements

* Detect implicit relative imports.
* Suggest using `setUpTestData()` instead of `setUp()`.
* Detect Python 2-only unittest asserts.
* Suggest using `io.open()` instead of `open()`.
* Support checking `unicode(some_variable)` case.
* Suggest `six.moves` counterparts of Python 2-only imports.
* Suggest `six.iter*()` counterparts of `dict.iter*()` methods.
