from lib2to3.fixer_base import BaseFix
from lib2to3.fixer_util import BlankLine


class FixFuture(BaseFix):
    PATTERN = r"""
        simple_stmt < import_from < 'from' module_name="__future__" 'import' any > '\n' >
    """

    def transform(self, node, results):
        # If there is one or more newline between __future__ import and
        # the next line, we want to remove them.
        node.next_sibling.prefix = node.next_sibling.prefix.lstrip()
        node.next_sibling.changed()
        new = BlankLine()
        new.prefix = node.prefix
        return new
