# coding: utf-8

import ast

import pycodestyle

__version__ = '0.1'


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
            'HLVE005': 'First argument of unicode() contains non-ASCII characters and decoding '
                       'it to unicode with ASCII encoding will raise UnicodeDecodeError.',
            'HLVE006': 'Do not use %%-formatting inside %s.%s().',
            'HLVE007': 'Do not use str.format() inside %s.%s().',
        }
    }

    def __init__(self):
        self.violations = []

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

    def report_error(self, node, code, args=None):
        message = self.messages['errors'].get(code)
        self._report_message(node, code, message, args)

    def report_warning(self, node, code, args=None):
        message = self.messages['warnings'].get(code)
        self._report_message(node, code, message, args)

    def _report_message(self, node, code, message, args=None):
        if args:
            message = message % args
        if message:
            message = '%s %s' % (code, message)
        self.violations.append((
            node.lineno,
            node.col_offset,
            message,
            type(self),
        ))


class HolviChecker(object):
    name = 'flake8-holvi'
    version = __version__

    def __init__(self, tree, filename):
        self.tree = tree
        self.filename = filename
        self.lines = None

    def load_file(self):
        if self.filename in ('stdin', '-', None):
            self.filename = 'stdin'
            self.lines = pycodestyle.stdin_get_value().splitlines(True)
        else:
            self.lines = pycodestyle.readlines(self.filename)

    def run(self):
        if not self.tree or not self.lines:
            self.load_file()
        self.tree = ast.parse(''.join(self.lines))
        visitor = HolviVisitor()
        visitor.visit(self.tree)
        for lineno, col_offset, message, rtype in visitor.violations:
            yield lineno, col_offset, message, rtype
