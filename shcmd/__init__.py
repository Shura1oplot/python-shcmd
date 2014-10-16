# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import sys
import os
import subprocess
import string
import re


__version_info__ = (0, 1, 0)
__version__ = ".".join(map(str, __version_info__))

__all__ = ("inline", "NOSEP", "NQ", "WQ", "SQ", "PUSHQ", "POPQ",
           "redirect", "append", "PIPE", "BG", "QUIET", "SILENT",
           "escape", "shcmd", "shell")


if sys.version_info[0] > 2:
    unicode = str
    orditer = iter

    def chriter(s):
        if isinstance(s, bytes):
            return (s[i:i+1] for i in range(len(s)))

        return iter(s)

else:
    def orditer(s):
        return (ord(c) for c in s)

    chriter = iter


escape_control = {"\a": "\\a", "\b": "\\b", "\t": "\\t", "\n": "\\n",
                  "\v": "\\v", "\f": "\\f", "\r": "\\r"}


class NoSepType(unicode):

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(NoSepType, cls).__new__(cls)

        return cls.__instance

    def __repr__(self):
        return "NOSEP"

NOSEP = NoSepType()


class inline(tuple):

    def __new__(cls, *args):
        if len(args) == 1 and isinstance(args[0], (tuple, list)):
            args = args[0]

        return super(inline, cls).__new__(cls, args)

    def __repr__(self):
        return "inline{}".format(super(inline, self).__repr__())


class QuotingFlag(unicode):

    __instances = {}

    def __new__(cls, s):
        if s not in cls.__instances:
            cls.__instances[s] = super(QuotingFlag, cls).__new__(cls, s)

        return cls.__instances[s]

    def __call__(self, *args):
        return inline((PUSHQ, self) + args + (POPQ, ))

    def __repr__(self):
        return unicode(self)

NQ = QuotingFlag("NQ")  # no quoting
WQ = QuotingFlag("WQ")  # weak quoting
SQ = QuotingFlag("SQ")  # strong quoting

PUSHQ = QuotingFlag("PUSHQ")  # push quoting
POPQ  = QuotingFlag("POPQ")   # pop quoting


def redirect(s, x=None):
    if x is None:
        s, x = ">", s

    if isinstance(x, int):
        if not re.match(r"^\d?[<>]$", s):
            raise ValueError("invalid redirect string")

        if not 0 <= x <= 9:
            raise ValueError("invalid descriptor")

        return NQ("{}&{}".format(s, x))

    if not re.match(r"^\d?([<>]>?|>\|)$", s):
        raise ValueError("invalid redirect string")

    return inline(NQ(s), NOSEP, x)


def append(filename):
    return redirect(">>", filename)


PIPE = NQ("|")
BG = NQ("&")
QUIET = redirect("/dev/null")
SILENT = inline(QUIET, redirect("2>", 1))


def shcmd(*args):
    if not args:
        return ""

    if len(args) == 1 and isinstance(args[0], (tuple, list)):
        args = args[0]

    quote_char = {NQ: "", WQ: '"', SQ: "'"}
    args = list(reversed(args))
    quoting = SQ
    stack = []
    result = []

    while True:
        try:
            arg = args.pop()
        except IndexError:
            break

        if isinstance(arg, inline):
            args.extend(reversed(arg))
            continue

        if arg is NOSEP:
            result.append(arg)
            continue

        if isinstance(arg, QuotingFlag):
            if arg is PUSHQ:
                stack.append(quoting)

            elif arg is POPQ:
                try:
                    quoting = stack.pop()
                except ValueError:
                    raise ValueError("qouting stack is empty")

            else:
                quoting = arg

            continue

        if not isinstance(arg, unicode):
            arg = unicode(arg)

        if result and result[-1] is not NOSEP:
            result.append(" ")

        need_quote = not arg
        buf = []

        for c in arg:
            if c in escape_control:
                need_quote = True
                buf.append(escape_control[c])

            elif c in frozenset(" \"#$&'()*;<=>?[\\]`{|}~"):
                need_quote = True

                if c == "\\":
                    buf.append("\\\\")

                elif quoting is WQ and c == '"':
                    buf.append('\\\"')

                elif quoting is SQ and c == "'":
                    buf.append("'\\''")

                else:
                    buf.append(c)

            else:
                buf.append(c)

        if need_quote:
            buf.append(quote_char[quoting])
            result.append(quote_char[quoting])

        result.extend(buf)

    return "".join(result)


if os.name == "posix":
    def shell(*args):
        return os.system(shcmd(*args))

elif os.name == "nt":
    def shell(*args):
        return subprocess.call(("bash.exe", "-c", shcmd(*args)))

else:
    def shell(*args):
        raise RuntimeError("unsupported platform: {}".format(os.name))


def escape(s, encoding=None, bash=False):
    encoded = False
    buf = []

    if isinstance(s, bytes):
        control = frozenset(x.encode("ascii") for x in escape_control)
        printable = frozenset(x.encode("ascii") for x in string.printable
                              if x == " " or x not in string.whitespace)

        for bc in chriter(s):
            if bc in control:
                buf.append(escape_control[bc.decode("ascii")])

            elif bc in printable:
                buf.append(bc.decode("ascii"))

            elif bash:
                encoded = True
                buf.append("\\x{:02X}".format(ord(bc)))

            else:
                buf.append("\\0{:03o}".format(ord(bc)))

    else:
        if encoding is None:
            encoding = "unicode" if bash else "utf-8"

        printable = frozenset(unicode(x) for x in string.printable
                              if x == " " or x not in string.whitespace)

        for uc in chriter(s):
            if uc in escape_control:
                buf.append(escape_control[uc])

            elif uc in printable:
                buf.append(uc)

            elif bash:
                encoded = True

                if encoding == "unicode":
                    buf.append("\\u{:04X}".format(ord(uc)))

                else:
                    buf.extend("\\x{:02X}".format(x)
                               for x in orditer(uc.encode(encoding)))

            else:
                buf.extend("\\0{:03o}".format(x)
                           for x in orditer(uc.encode(encoding)))

    if not bash or not encoded:
        return "".join(buf)

    for i, x in enumerate(buf):
        if x == "'":
            buf[i] = "'\\''"

    return NQ("$'{}'".format("".join(buf)))
