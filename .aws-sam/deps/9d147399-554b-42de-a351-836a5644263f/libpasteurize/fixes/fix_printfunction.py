"""
Fixer for print: from __future__ import print_function.
"""

from lib2to3 import fixer_base
from libfuturize.fixer_util import future_import


class FixPrintfunction(fixer_base.BaseFix):

    # explicit = True

    PATTERN = """
              power< 'print' trailer < '(' any* ')' > any* >
              """

    def transform(self, node, results):
        future_import("print_function", node)
