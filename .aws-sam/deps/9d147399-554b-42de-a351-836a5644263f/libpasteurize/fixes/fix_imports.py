"""
Fixer for standard library imports renamed in Python 3
"""

from lib2to3 import fixer_base
from lib2to3.fixer_util import Name, is_probably_builtin, Newline, does_tree_import
from lib2to3.pygram import python_symbols as syms
from lib2to3.pgen2 import token
from lib2to3.pytree import Node, Leaf

from libfuturize.fixer_util import touch_import_top

# from ..fixer_util import NameImport

# used in simple_mapping_to_pattern()
MAPPING = {
    "reprlib": "repr",
    "winreg": "_winreg",
    "configparser": "ConfigParser",
    "copyreg": "copy_reg",
    "queue": "Queue",
    "socketserver": "SocketServer",
    "_markupbase": "markupbase",
    "test.support": "test.test_support",
    "dbm.bsd": "dbhash",
    "dbm.ndbm": "dbm",
    "dbm.dumb": "dumbdbm",
    "dbm.gnu": "gdbm",
    "html.parser": "HTMLParser",
    "html.entities": "htmlentitydefs",
    "http.client": "httplib",
    "http.cookies": "Cookie",
    "http.cookiejar": "cookielib",
    #          "tkinter": "Tkinter",
    "tkinter.dialog": "Dialog",
    "tkinter._fix": "FixTk",
    "tkinter.scrolledtext": "ScrolledText",
    "tkinter.tix": "Tix",
    "tkinter.constants": "Tkconstants",
    "tkinter.dnd": "Tkdnd",
    "tkinter.__init__": "Tkinter",
    "tkinter.colorchooser": "tkColorChooser",
    "tkinter.commondialog": "tkCommonDialog",
    "tkinter.font": "tkFont",
    "tkinter.ttk": "ttk",
    "tkinter.messagebox": "tkMessageBox",
    "tkinter.turtle": "turtle",
    "urllib.robotparser": "robotparser",
    "xmlrpc.client": "xmlrpclib",
    "builtins": "__builtin__",
}

# generic strings to help build patterns
# these variables mean (with http.client.HTTPConnection as an example):
# name = http
# attr = client
# used = HTTPConnection
# fmt_name is a formatted subpattern (simple_name_match or dotted_name_match)

# helps match 'queue', as in 'from queue import ...'
simple_name_match = "name='%s'"
# helps match 'client', to be used if client has been imported from http
subname_match = "attr='%s'"
# helps match 'http.client', as in 'import urllib.request'
dotted_name_match = "dotted_name=dotted_name< %s '.' %s >"
# helps match 'queue', as in 'queue.Queue(...)'
power_onename_match = "%s"
# helps match 'http.client', as in 'http.client.HTTPConnection(...)'
power_twoname_match = "power< %s trailer< '.' %s > any* >"
# helps match 'client.HTTPConnection', if 'client' has been imported from http
power_subname_match = "power< %s any* >"
# helps match 'from http.client import HTTPConnection'
from_import_match = "from_import=import_from< 'from' %s 'import' imported=any >"
# helps match 'from http import client'
from_import_submod_match = "from_import_submod=import_from< 'from' %s 'import' (%s | import_as_name< %s 'as' renamed=any > | import_as_names< any* (%s | import_as_name< %s 'as' renamed=any >) any* > ) >"
# helps match 'import urllib.request'
name_import_match = "name_import=import_name< 'import' %s > | name_import=import_name< 'import' dotted_as_name< %s 'as' renamed=any > >"
# helps match 'import http.client, winreg'
multiple_name_import_match = (
    "name_import=import_name< 'import' dotted_as_names< names=any* > >"
)


def all_patterns(name):
    """
    Accepts a string and returns a pattern of possible patterns involving that name
    Called by simple_mapping_to_pattern for each name in the mapping it receives.
    """

    # i_ denotes an import-like node
    # u_ denotes a node that appears to be a usage of the name
    if "." in name:
        name, attr = name.split(".", 1)
        simple_name = simple_name_match % (name)
        simple_attr = subname_match % (attr)
        dotted_name = dotted_name_match % (simple_name, simple_attr)
        i_from = from_import_match % (dotted_name)
        i_from_submod = from_import_submod_match % (
            simple_name,
            simple_attr,
            simple_attr,
            simple_attr,
            simple_attr,
        )
        i_name = name_import_match % (dotted_name, dotted_name)
        u_name = power_twoname_match % (simple_name, simple_attr)
        u_subname = power_subname_match % (simple_attr)
        return " | \n".join((i_name, i_from, i_from_submod, u_name, u_subname))
    else:
        simple_name = simple_name_match % (name)
        i_name = name_import_match % (simple_name, simple_name)
        i_from = from_import_match % (simple_name)
        u_name = power_onename_match % (simple_name)
        return " | \n".join((i_name, i_from, u_name))


class FixImports(fixer_base.BaseFix):

    PATTERN = " | \n".join([all_patterns(name) for name in MAPPING])
    PATTERN = " | \n".join((PATTERN, multiple_name_import_match))

    def transform(self, node, results):
        touch_import_top("future", "standard_library", node)
