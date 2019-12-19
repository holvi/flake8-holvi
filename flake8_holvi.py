# coding: utf-8

import ast

import pycodestyle

__version__ = '0.1'

python2_modules_map = {
    # Python 2 module - six.moves counterpart
    '__builtin__': 'builtins',
    'BaseHTTPServer': 'BaseHTTPServer',
    'ConfigParser': 'configparser',
    'HTMLParser': 'html_parser',
    'Queue': 'queue',
    'SimpleHTTPServer': 'SimpleHTTPServer',
    'cPickle': 'cPickle',
    'cStringIO': 'cStringIO',
    'cookielib': 'http_cookiejar',
    'cookie': 'http_cookies',
    'htmlentitydefs': 'html_entities',
    'httplib': 'http_client',
    'urlparse': 'urllib.parse',
}

python2_unittest_assertions = {
    # Python 2 assertion - six counterpart
    'assertItemsEqual': 'assertCountEqual',
    'assertRaisesRegexp': 'assertRaisesRegex',
    'assertRegexpMatches': 'assertRegex',
}


def _detect_unicode_decode_error(value, encoding=None):
    try:
        if encoding:
            unicode(value, encoding)
        else:
            unicode(value)
    except UnicodeDecodeError:
        return True
    else:
        return False


class HolviVisitor(ast.NodeVisitor):

    messages = {
        'warnings': {
            'HLVW001': 'First argument of unicode() may contain non-ASCII characters. '
                       'We recommend passing encoding explicitly.',
            'HLVW002': 'trying to decode str with ASCII encoding may not work',
        },
        'errors': {
            'HLVE001': 'Import print_function __future__ import and use print().',
            'HLVE002': 'unicode() is renamed to str() in Python 3. Use six.text_type() instead.',
            'HLVE003': 'str() is renamed to bytes() in Python 3. Use six.binary_type() instead.',
            'HLVE004': 'First argument of unicode() contains non-ASCII characters and it '
                       'will raise UnicodeDecodeError. Pass encoding explicitly.',
            'HLVE005': 'First argument of unicode() contains non-ASCII characters and trying to '
                       'decode it to unicode with ASCII encoding will raise UnicodeDecodeError.',
            'HLVE006': 'Do not use %%-formatting inside %s.%s().',
            'HLVE007': 'Do not use str.format() inside %s.%s().',
            'HLVE008': '%r must be passed to the lambda to avoid late binding issue in Python.',
            'HLVE009': 'Replace Python 2-only import %r with six.moves.%s.',
            'HLVE010': 'Replace Python 2-only unittest assertion %r with six.%s.',
        }
    }

    def __init__(self, ignore_warnings=False):
        self.ignore_warnings = ignore_warnings
        self.violations = []
        self.violation_codes = []

        # TODO: Consider using proper stacks here.
        self._inside_for_node = None
        self._lambda_node = None
        self._detect_late_binding = False

    def visit_Print(self, node):
        self.report_error(node, 'HLVE001')

    def visit_Call(self, node):
        func = getattr(node, 'func', None)
        func_name = getattr(func, 'id', None)
        func_value = getattr(func, 'value', None)
        # unicode(...)
        if func and func_name == 'unicode':
            self.report_error(node, 'HLVE002')
            value = getattr(node.args[0], 's', None)
            # unicode('non-ascıı')
            if len(node.args) == 1 and isinstance(value, str):
                if _detect_unicode_decode_error(value):
                    self.report_error(node, 'HLVE004')
                else:
                    self.report_warning(node, 'HLVW001')

            # unicode('ı', 'ascii')
            elif len(node.args) == 2 and isinstance(value, str) and node.args[1].s == 'ascii':
                if _detect_unicode_decode_error(value, 'ascii'):
                    self.report_error(node, 'HLVE005')
                else:
                    self.report_warning(node, 'HLVW002')

            # TODO: Detect unicode(..., encoding='...') too.

        # str(...)
        elif func and func_name == 'str':
            self.report_error(node, 'HLVE003')
            # TODO: str(u"aaaı")

        # logging.debug('%s' % 'a')
        # logger.error('%s' % 'a')
        # logging.debug('{}'.format('a'))
        # logger.warning('{}'.format('a'))
        elif func and getattr(func_value, 'id', None) in ('logger', 'logging'):
            logging_methods = ('debug', 'info', 'warning', 'error', 'critical', 'exception')
            if getattr(func, 'attr', None) in logging_methods:
                # %-format
                if len(node.args) and isinstance(node.args[0], ast.BinOp):
                    self.report_error(node, 'HLVE006', args=(func_value.id, func.attr))
                # str.format()
                elif (
                    len(node.args) and isinstance(node.args[0], ast.Call)
                        and getattr(node.args[0].func, 'attr', None) == 'format'
                ):
                    self.report_error(node, 'HLVE007', args=(func_value.id, func.attr))
        # Traverse all child nodes.
        self.generic_visit(node)

    def visit_For(self, node):
        self._inside_for_node = node
        self.generic_visit(node)

    def visit_Lambda(self, node):
        if self._inside_for_node is not None:
            if isinstance(node.body, ast.Call):
                self._detect_late_binding = True
                self._lambda_node = node
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if self._detect_late_binding:
            for_node = self._inside_for_node
            target = for_node.target.id
            name = node.value.id
            if target == name:
                defaults = self._lambda_node.args.defaults
                # lambda: target
                if not defaults:
                    self.report_error(node, 'HLVE008', args=(target,))
                # lambda foo=foo: target or lambda foo=foo: target, foo
                elif len(defaults) == 1:
                    found = False
                    for d in defaults:
                        if d.id == target:
                            found = True
                            break
                    if not found:
                        # TODO: Perhaps add a more descriptive message?
                        self.report_error(node, 'HLVE008', args=(target,))
        else:
            method_name = node.attr
            if (
                isinstance(node.value, ast.Name) and
                node.value.id == 'self' and
                method_name in python2_unittest_assertions
            ):
                self.report_error(
                    node,
                    'HLVE010',
                    args=(method_name, python2_unittest_assertions[method_name]),
                )
        self.generic_visit(node)

    def visit_Import(self, node):
        for name in node.names:
            mod_name = name.name
            if mod_name in python2_modules_map:
                self.report_error(
                    node,
                    'HLVE009',
                    args=(mod_name, python2_modules_map[mod_name]),
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        mod_name = node.module
        if mod_name in python2_modules_map:
            self.report_error(
                node,
                'HLVE009',
                args=(mod_name, python2_modules_map[mod_name]),
            )
        self.generic_visit(node)

    def report_error(self, node, code, args=None):
        message = self.messages['errors'].get(code)
        self._report_message(node, code, message, args)

    def report_warning(self, node, code, args=None):
        if self.ignore_warnings:
            return
        message = self.messages['warnings'].get(code)
        self._report_message(node, code, message, args)

    @staticmethod
    def _format_message(code, message, args=None):
        if args:
            message = message % args
        if message:
            message = '%s %s' % (code, message)
        return message

    def _report_message(self, node, code, message, args=None):
        message = self._format_message(code, message, args)
        self.violations.append((
            node.lineno,
            node.col_offset,
            message,
            type(self),
        ))
        self.violation_codes.append(code)


class HolviChecker(object):
    name = 'flake8-holvi'
    version = __version__

    def __init__(self, tree, filename, lines):
        self.tree = tree
        self.filename = filename
        self.lines = lines

        # Default settings.
        self.ignore_warnings = False

    @classmethod
    def add_options(cls, parser):
        parser.add_option(
            '--ignore-warnings',
            action='store_true',
            parse_from_config=True,
            default=False,
            help='Do not report checks added as warnings.'
        )

    @classmethod
    def parse_options(cls, options):
        cls.ignore_warnings = options.ignore_warnings

    def load_file(self):
        if self.filename in ('stdin', '-', None):
            self.filename = 'stdin'
            self.lines = pycodestyle.stdin_get_value().splitlines(True)
        else:
            self.lines = pycodestyle.readlines(self.filename)

    def run(self):
        if not self.tree and not self.lines:
            self.load_file()
        self.tree = ast.parse(''.join(self.lines))
        visitor = HolviVisitor(self.ignore_warnings)
        visitor.visit(self.tree)
        for lineno, col_offset, message, rtype in visitor.violations:
            if pycodestyle.noqa(self.lines[lineno - 1]):
                continue
            yield lineno, col_offset, message, rtype
