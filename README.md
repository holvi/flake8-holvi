# flake8-holvi

## Installation and usage

It's not uploaded to our PyPI server yet. The only way to install it is from GitHub:

```bash
$ pip install -e git+https://github.com/holviberker/flake8-holvi.git#egg=flake8-holvi
```

You don't need to do anything else to be able to use it. However, you can use the
`--select` option if you want to see violations found flake8-holvi:

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
   # Correct usage:
   unicode('text with non-ASCII characters: ıçğüş', 'utf-8')
   ```

3. ```py
   # Should be used a non-ASCII encoding.
   unicode('text with non-ASCII characters: ıçğüş', 'ascii')
   # Correct usage:
   unicode('text with non-ASCII characters: ıçğüş', 'utf-8')
   ```

4. ```py
   logger.debug('Some debug information: %s' % foo)
   # Correct usage:
   logger.debug('Some debug information: %s', foo)
   ```

5. ```py
   logger.debug('Some debug information: {}'.format(foo))
   # Correct usage:
   logger.debug('Some debug information: %s', foo)
   ```

6. ```py
   str(...)  # Should be replaced with six.binary_type().
   ```

### Warnings

1. ```py
   # Patentially dangerous usage:
   ascii_only_content = get_data_from_external_api()
   unicode(ascii_only_content)
   # Safer usage since the default string encoding is 'ascii' in
   # Python 2 and get_data_from_external_api() can return non-ASCII
   # data:
   unicode(ascii_only_content, 'utf-8')
   ```

2. ```py
   # Patentially dangerous usage:
   ascii_only_content = get_data_from_external_api()
   unicode(ascii_only_content, 'ascii')
   # 'ascii' should be passed only if we 100% sure ascii_only_content
   # will always be ASCII-only. Otherwise use a more appropriote encoding:
   unicode(ascii_only_content, better_encoding)
   ```

## Possible future improvements

1. Detect implicit relative imports.
2. Suggest using `setUpTestData()` instead of `setUp()`.
3. Detect Python 2-only unittest asserts.
4. Suggest using `io.open()` instead of `open()`.
