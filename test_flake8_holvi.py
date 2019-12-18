# coding: utf-8
from __future__ import print_function

import ast
import textwrap
import unittest

from flake8_holvi import HolviChecker
from flake8_holvi import HolviVisitor


class BaseTestCase(unittest.TestCase):

    print_violations = False

    def assertSourceViolates(self, source, violations_codes=None):
        if not violations_codes:
            raise ValueError('violations keyword-argument must be passed')
        source = textwrap.dedent(source)
        tree = ast.parse(source)
        visitor = HolviVisitor()
        visitor.visit(tree)
        found_violations = visitor.violation_codes
        if self.print_violations:
            print()
            print(found_violations)
            print()
        self.assertItemsEqual(found_violations, violations_codes)


class HolviVisitorErrorsTestCase(BaseTestCase):

    def test_print(self):
        source = """
        print 'yes'
        """
        self.assertSourceViolates(source, ['HLVE001'])

    def test_unicode(self):
        source = """
        foo = unicode('bar')
        """
        self.assertSourceViolates(source, ['HLVE002', 'HLVW001'])

    def test_bytes(self):
        source = """
        foo = u'foo'
        bar = str(foo)
        """
        self.assertSourceViolates(source, ['HLVE003'])

    def test_unicode_encoding(self):
        # TODO: Support a = 'ı'; b = unicode(a) too.
        source = """
        foo = unicode('ı')
        """
        self.assertSourceViolates(source, ['HLVE004', 'HLVE002'])

    def test_unicode_encoding_ascii(self):
        source = """
        foo = unicode('ı', 'ascii')
        """
        self.assertSourceViolates(source, ['HLVE005', 'HLVE002'])

    def test_logging_percent_formatting(self):
        source = """
        logging.info('some %s' % stuff)
        """
        self.assertSourceViolates(source, ['HLVE006'])

    def test_logging_str_format(self):
        source = """
        logging.info('some {}'.format(stuff))
        """
        self.assertSourceViolates(source, ['HLVE007'])


class HolviCheckerTestCase(BaseTestCase):

    def assertRunPlugin(self, source, violations_codes=None):
        if not violations_codes:
            raise ValueError('violations keyword-argument must be passed')
        lines = textwrap.dedent(source).splitlines(True)
        tree = ast.parse(''.join(lines))
        plugin = HolviChecker(tree, None, lines)
        found_violations = [v[2] for v in plugin.run()]
        expected_violations = []
        for v in violations_codes:
            if v.startswith('HLVE'):
                expected_violations.append(
                    HolviVisitor._format_message(
                        v,
                        HolviVisitor.messages['errors'].get(v),
                    )
                )
            elif v.startswith('HLVW'):
                expected_violations.append(
                    HolviVisitor._format_message(
                        v,
                        HolviVisitor.messages['warnings'].get(v),
                    )
                )
        self.assertItemsEqual(found_violations, expected_violations)

    def test_skip_noqa(self):
        source = """
        stuff = unicode(stuff)
        logging.info('some {}'.format(stuff))  # noqa
        """
        self.assertRunPlugin(source, ['HLVE002'])
