# coding: utf-8

import ast

import pycodestyle

__version__ = '0.2.0'

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

# TODO: make this configurable via CLI or flake8 config.
potential_implicit_relative_imports = {
    'exceptions',
    'models',
    'serializers',
    'signals',
    'tasks',
    'views',
    # Holvi-specific modules:
    'api',
    'constants',
    'providers',
}


class HolviVisitor(ast.NodeVisitor):

    messages = {
        'warnings': {
            'HLVW301': 'First argument of unicode() may contain non-ASCII characters. '
                       'We recommend passing encoding explicitly.',
        },
        'errors': {
            'HLVE006': 'Do not use %%-formatting inside %s.%s().',
            'HLVE007': 'Do not use str.format() inside %s.%s().',
            'HLVE008': '%r must be passed to the lambda to avoid late binding issue in Python.',
            'HLVE012': '%r cannot be found in lambda\'s default argument(s).',
            'HLVE301': 'Import print_function from __future__ and use print().',
            'HLVE302': 'unicode() is renamed to str() in Python 3. Use six.text_type() instead.',
            'HLVE303': 'str() is renamed to bytes() in Python 3. Use six.binary_type() instead.',
            'HLVE309': 'Replace Python 2-only import %r with six.moves.%s.',
            'HLVE310': 'Replace Python 2-only unittest assertion %r with six.%s.',
            'HLVE311': 'Replace implicit relative import %r with %r.',
        }
    }

    def __init__(self, ignore_warnings=False):
        self.ignore_warnings = ignore_warnings
        self.violations = []
        self.violation_codes = []

        self._inside_for_node = None

    def visit_Print(self, node):
        self.report_error(node, 'HLVE301')

    def visit_Call(self, node):
        func = getattr(node, 'func', None)
        func_name = getattr(func, 'id', None)
        func_value = getattr(func, 'value', None)
        # unicode(...)
        if func and func_name == 'unicode':
            self.report_error(node, 'HLVE302')
            value = getattr(node.args[0], 's', None)
            # unicode('non-ascıı')
            if len(node.args) == 1 and isinstance(value, str):
                self.report_warning(node, 'HLVW301')

        # str(...)
        elif func and func_name == 'str':
            self.report_error(node, 'HLVE303')
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
        self._inside_for_node = None

    def visit_Lambda(self, node):
        if self._inside_for_node is not None:
            if isinstance(node.body, ast.Call) and isinstance(node.body.func, ast.Attribute):
                # Get the name of control variable from 'for <control_variable> in ...'.
                if 'id' not in self._inside_for_node.target._fields:  # pragma: no cover
                    # TODO: We don't support 'for i, j in ...' yet.
                    return
                control_variable = self._inside_for_node.target.id
                # Default arguments passed to lambda: 'lambda foo=foo: ...'
                defaults = node.args.defaults
                for arg in node.body.args:
                    # Check if arg is ast.List, ast.Tuple, or ast.Set.
                    if 'elts' in arg._fields:
                        elts = arg.elts
                        for e in elts:
                            # Look for ast.Attribute nodes.
                            if 'value' in e._fields and e.value.id == control_variable:
                                if len(defaults) == 0:
                                    # control variable isn't passed to lambda.
                                    self.report_error(node, 'HLVE008', args=(control_variable,))
                                elif len(defaults) > 0:
                                    # There is a default argument passed, let's check it's used at all.
                                    found = False
                                    for d in defaults:
                                        # TODO: check Attribute node for lambda foo=bar.baz: ...
                                        # We only look for Name nodes now.
                                        if 'id' in d._fields and d.id == control_variable:
                                            found = True
                                            break
                                    if not found:
                                        self.report_error(node, 'HLVE012', args=(control_variable,))
                            # Look for ast.Name nodes.
                            elif 'id' in e._fields and e.id == control_variable:
                                if len(defaults) == 0:
                                    # Control variable isn't passed to lambda.
                                    self.report_error(node, 'HLVE008', args=(control_variable,))
                                elif len(defaults) > 1:  # pragma: no cover
                                    assert False, 'implement this for ast.Tuple etc.'
                    # Check if arg is ast.Attribute.
                    elif 'value' in arg._fields:
                        if arg.value.id == control_variable:
                            if len(defaults) == 0:
                                # Control variable isn't passed to lambda.
                                self.report_error(node, 'HLVE008', args=(control_variable,))
                            elif len(defaults) > 1:  # pragma: no cover
                                assert False, 'implement this for ast.Attribute'
                    # Check if arg is ast.Name.
                    elif 'id' in arg._fields:
                        if arg.id == control_variable:
                            if len(defaults) == 0:
                                # Control variable isn't passed to lambda.
                                self.report_error(node, 'HLVE008', args=(control_variable,))
                            elif len(defaults) > 1:  # pragma: no cover
                                assert False, 'implement this for ast.Name'
        self.generic_visit(node)

    def visit_Attribute(self, node):
        method_name = node.attr
        if (
            isinstance(node.value, ast.Name) and
            node.value.id == 'self' and
            method_name in python2_unittest_assertions
        ):
            self.report_error(
                node,
                'HLVE310',
                args=(method_name, python2_unittest_assertions[method_name]),
            )
        self.generic_visit(node)

    def visit_Import(self, node):
        for name in node.names:
            mod_name = name.name
            if mod_name in python2_modules_map:
                self.report_error(
                    node,
                    'HLVE309',
                    args=(mod_name, python2_modules_map[mod_name]),
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        mod_name = node.module
        if mod_name in python2_modules_map:
            self.report_error(
                node,
                'HLVE309',
                args=(mod_name, python2_modules_map[mod_name]),
            )
        # Ignore explicit relative imports.
        elif node.level == 0 and mod_name in potential_implicit_relative_imports:
            self.report_error(
                node,
                'HLVE311',
                args=(mod_name, '.%s' % mod_name),
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
