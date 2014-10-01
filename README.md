shcmd
=====

Python 2/3 module which integrates shell (POSIX-compatible or bash) with python. It converts list of args into valid and correct quoted shell command. Weak and strong quoting are support.

Examples
========
```
>>> from shcmd import *
>>> shcmd("ls", "-l")
'ls -l'
>>> print(shcmd("echo", "O'Connor"))
echo 'O'\''Connor'
>>> print(shcmd("echo", "O`Connor"))
echo 'O`Connor'
>>> print(shcmd("echo", "$100"))
echo '$100'
>>> print(shcmd("echo", WQ, "$PATH"))
echo "$PATH"
>>> print(shcmd("echo", WQ("$PATH"), NQ("|"), "tr", ":", "\n"))
echo "$PATH" | tr : '\n'
>>> print(shcmd("cat", "test.lst", PIPE, "wc", "-l"))
cat test.lst | wc -l
>>> print(shcmd("./foobar", redirect(">>", "foobar.log")))
./foobar >>foobar.log
>>> print(shcmd("./foobar", redirect(">", "/dev/null"), redirect("2>", 1)))
./foobar >/dev/null 2>&1
>>> print(shcmd("./foobar", QUIET))
./foobar >/dev/null
>>> print(shcmd("./foobar", SILENT))
./foobar >/dev/null 2>&1
>>> print(shcmd("tar", "cf", "-", ".", PIPE, "gzip", "-f9", redirect("../backup.tar.gz"), BG))
tar cf - . | gzip -f9 >../backup.tar.gz &
>>> print(shcmd(NQ("SOMEVAR=1"), "sh", "-c", shcmd("echo", WQ("$SOMEVAR"))))
SOMEVAR=1 sh -c 'echo "$SOMEVAR"'
>>> escape("друг!")
'\\0320\\0264\\0321\\0200\\0321\\0203\\0320\\0263!'
>>> escape("друг!", bash=True)
inline(PUSHQ, NQ, "$'\\u0434\\u0440\\u0443\\u0433!'", POPQ)
>>> escape("друг!", encoding="utf-8", bash=True)
inline(PUSHQ, NQ, "$'\\xD0\\xB4\\xD1\\x80\\xD1\\x83\\xD0\\xB3!'", POPQ)
```

Usage
=====
`shcmd(*args)` converts list of args into correct quoted shell command. Additional objects can be used to control function behavior:
 * `inline(*args)` - (foo, inline(bar, baz), spam) == (foo, bar, baz, spam). Is good to store frequently used parts of code.
 * `NOSEP` - Do not insert separator between arguments (example: `shcmd("foo", NOSEP, "bar") -> "foobar"`)
 * `NQ` - No Quoting - disable any quoting
 * `WQ` - Weak Qouting - use double quotes
 * `SQ` - Strong Quotes - use single quotes
 * `PUSHQ` - save current quoting mode in quoting stack
 * `POPQ` - restore quoting mode from quoting stack
 * `NQ(*args)`, `WQ(*args)`, `SQ(*args)` - save current quoting mode, switch quoting mode to NQ|WQ|SQ, inline args, restore saved quoting mode (example: `WQ("$PATH") -> inline(PUSHQ, WQ, "$PATH", POPQ)`)
 * `redirect(x)` - redirect stdout to file or descriptor (`>filename`)
 * `append(x)` - appending redirect stdout to file (`>>filename`)
 * `redirect(s, x)` - user defined redirection rule (example: `redirect("2>", 1) -> NQ("2>&1")`)
 * `PIPE` - `NQ("|")`
 * `BG` - NQ("&")
 * `QUIET` - `redirect("/dev/null")`
 * `SILENT` - `inline(QUIET, redirect("2>", 1))`

`shell(*args)` - calls `shcmd(*args)` and executes the result.

`escape(s, encoding=None, bash=False)` converts unicode string or bytes object into POSIX-compatible shell or bash escaped string. Default encodings are utf-8 for POSIX-compatible shells and unicode for bash. See examples, `bash` and `sh` man pages for additional information.
