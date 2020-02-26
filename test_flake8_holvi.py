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
            violations_codes = []
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
        self.assertSourceViolates(source, ['HLVE301'])

    def test_unicode(self):
        source = """
        foo = unicode('bar')
        """
        self.assertSourceViolates(source, ['HLVE302', 'HLVW301'])

    def test_bytes(self):
        source = """
        foo = u'foo'
        bar = str(foo)
        """
        self.assertSourceViolates(source, ['HLVE303'])

    def test_unicode_encoding(self):
        source = """
        foo = unicode('ı')
        """
        self.assertSourceViolates(source, ['HLVW301', 'HLVE302'])

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

    def test_late_binding_1(self):
        source = """
        for event in events:
            transaction.on_commit(lambda: task.apply_async((event.id,)))
        """
        self.assertSourceViolates(source, ['HLVE008'])

    def test_late_binding_2(self):
        source = """
        for event in events:
            transaction.on_commit(lambda: task.apply_async((event,)))
        """
        self.assertSourceViolates(source, ['HLVE008'])

    def test_late_binding_4(self):
        source = """
        for event in events:
            transaction.on_commit(lambda user=user: task.apply_async((event.id, user.email)))
        """
        self.assertSourceViolates(source, ['HLVE012'])

    def test_late_binding_5(self):
        source = """
        for event in events:
            transaction.on_commit(lambda user=user: task.apply_async((event.id,)))
        """
        self.assertSourceViolates(source, ['HLVE012'])

    def test_late_binding_6(self):
        source = """
        for event in events:
            transaction.on_commit(lambda user_id=user.id: task.apply_async((event.id, user_id)))
        """
        self.assertSourceViolates(source, ['HLVE012'])

    def test_late_binding_7(self):
        source = """
        for obj in queryset:
            connection.on_commit(lambda: send_invoice.delay(obj.id, sent_by, language))
        """
        self.assertSourceViolates(source, ['HLVE008'])

    def test_late_binding_8(self):
        source = """
        for obj in queryset:
            connection.on_commit(lambda: send_invoice.delay(obj))
        """
        self.assertSourceViolates(source, ['HLVE008'])

    def test_late_no_error_1(self):
        source = """
        for event in events:
            transaction.on_commit(lambda foo=event: task.apply_async((foo,)))
        """
        self.assertSourceViolates(source)

    def test_late_no_error_2(self):
        source = """
        for event in events:
            transaction.on_commit(lambda event=event: task.apply_async((event.id,)))
        """
        self.assertSourceViolates(source)

    def test_late_no_error_3(self):
        source = """
        for event in events:
            transaction.on_commit(lambda event=event: validate_event((event,)))
        """
        self.assertSourceViolates(source)

    def test_python2_imports(self):
        source = """
        import urlparse
        """
        self.assertSourceViolates(source, ['HLVE309'])

        source = """
        import urlparse as something_else
        """
        self.assertSourceViolates(source, ['HLVE309'])

        source = """
        from urlparse import urlparse
        """
        self.assertSourceViolates(source, ['HLVE309'])

        source = """
        from urlparse import urlparse as py_urlparse
        """
        self.assertSourceViolates(source, ['HLVE309'])

    def test_python2_unittest_assertions(self):
        source = """
        class MyTestCase(unittest.TestCase):
            def test_foo(self):
                self.assertItemsEqual([], [])
        """
        self.assertSourceViolates(source, ['HLVE310'])

    def test_implicit_relative_imports(self):
        source = """
        from models import User
        """
        self.assertSourceViolates(source, ['HLVE311'])

        source = """
        from models import User
        from tasks import send_welcome_email
        """
        self.assertSourceViolates(source, ['HLVE311', 'HLVE311'])

        source = """
        from .models import User
        """
        self.assertSourceViolates(source)

        source = """
        from django.db import models
        """
        self.assertSourceViolates(source)

    def test_detect_empty_docstring_in_function(self):
        source = """
        def foo():
            ''''''
            return 42
        """
        self.assertSourceViolates(source, ['HLVE013'])

        source = """
        def foo():
            '''
            '''
            return 42
        """
        self.assertSourceViolates(source, ['HLVE013'])

        source = """
        def foo():
            ''''''
            def bar():
                ''''''
                return -1
            return bar(), 42
        """
        self.assertSourceViolates(source, ['HLVE013', 'HLVE013'])

        source = """
        def foo():
            def bar():
                ''''''
                return -1
            return bar
        """
        self.assertSourceViolates(source, ['HLVE013'])

        source = """
        def foo():
            return 42
        """
        self.assertSourceViolates(source, [])

    def test_detect_empty_docstring_in_class(self):
        source = """
        class Spam(object):
            ''''''
            pass
        """
        self.assertSourceViolates(source, ['HLVE013'])

        source = """
        class Spam:
            ''''''
            pass
        """
        self.assertSourceViolates(source, ['HLVE013'])

        source = """
        class Spam(object):
            '''
            '''
            pass
        """
        self.assertSourceViolates(source, ['HLVE013'])

        source = """
        class Spam(object):
            '''
            '''

            def method(self):
                ''''''
        """
        self.assertSourceViolates(source, ['HLVE013', 'HLVE013'])

        source = """
        class Spam(object):

            @classmethod
            def class_method(cls):
                ''''''
        """
        self.assertSourceViolates(source, ['HLVE013'])

        source = """
        class Spam(object):

            @staticmethod
            def static_method():
                ''''''
        """
        self.assertSourceViolates(source, ['HLVE013'])

        source = """
        class Spam(object):
            '''
            '''

            class Meta:
                ''''''
                foo = object()
        """
        self.assertSourceViolates(source, ['HLVE013', 'HLVE013'])

    def test_detect_empty_docstring_in_module(self):
        source = """
        ''''''

        import argparse

        CONSTANT = 42
        """
        self.assertSourceViolates(source, ['HLVE013'])

        source = """
        '''
        
        '''

        CONSTANT = 42
        """
        self.assertSourceViolates(source, ['HLVE013'])


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
        self.assertRunPlugin(source, ['HLVE302'])
