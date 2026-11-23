"""Strip comments from C# source, so a name mentioned in prose is not counted as an implementation.

WHY THIS EXISTS, and why the existing tools were not enough:

async_method_coverage.py and absent_by_leverage.py both scan raw source text, so a doc comment saying "the image names
SubmitWebRtc" makes SubmitWebRtc count as present. R914 produced exactly that: the coverage figure rose by one and the
one was my own comment. The tools were written that way because the alternative -- parsing C# -- is more work, and
because until a round started quoting image names in comments the error never bit.

Why not a real parser: the comments that matter here are C#'s three forms and the strings that can contain something
that looks like a comment. A character scanner that tracks string, verbatim string, raw string and character literals
gets all four right; a regex cannot, because "http://x" inside a string literal would lose its tail to a // comment
strip. The scan below is twenty lines and needs no dependency.

Not a general C# lexer: interpolation holes, preprocessor branches and raw-string delimiter counts beyond three quotes
are not modelled. Those gaps can only cause a name to be counted as absent when it is present, which this tool reports
as a separate figure rather than hiding.
"""

import io
import os
import re

ROOT = r"D:\projects\cyber-reverse\replica"


def strip_comments(src):
    """Remove // and /* */ comments and leave everything else, including string literals, intact."""
    out = []
    i = 0
    n = len(src)
    while i < n:
        ch = src[i]

        # line comment
        if ch == "/" and i + 1 < n and src[i + 1] == "/":
            while i < n and src[i] not in "\r\n":
                i += 1
            continue

        # block comment
        if ch == "/" and i + 1 < n and src[i + 1] == "*":
            i += 2
            while i + 1 < n and not (src[i] == "*" and src[i + 1] == "/"):
                i += 1
            i += 2
            continue

        # raw string literal: three or more quotes
        if ch == '"' and src.startswith('"""', i):
            quotes = 0
            while i + quotes < n and src[i + quotes] == '"':
                quotes += 1
            close = '"' * quotes
            start = i
            i += quotes
            while i < n and not src.startswith(close, i):
                i += 1
            i = min(n, i + quotes)
            out.append(src[start:i])
            continue

        # verbatim string
        if ch == "@" and i + 1 < n and src[i + 1] == '"':
            start = i
            i += 2
            while i < n:
                if src[i] == '"' and i + 1 < n and src[i + 1] == '"':
                    i += 2
                    continue
                if src[i] == '"':
                    i += 1
                    break
                i += 1
            out.append(src[start:i])
            continue

        # ordinary string
        if ch == '"':
            start = i
            i += 1
            while i < n:
                if src[i] == "\\":
                    i += 2
                    continue
                if src[i] == '"':
                    i += 1
                    break
                i += 1
            out.append(src[start:i])
            continue

        # character literal
        if ch == "'":
            start = i
            i += 1
            while i < n:
                if src[i] == "\\":
                    i += 2
                    continue
                if src[i] == "'":
                    i += 1
                    break
                i += 1
            out.append(src[start:i])
            continue

        out.append(ch)
        i += 1
    return "".join(out)


def sources():
    for dp, _dirs, fs in os.walk(os.path.join(ROOT, "src")):
        if os.sep + "obj" + os.sep in dp or os.sep + "bin" + os.sep in dp:
            continue
        for fn in fs:
            if fn.endswith(".cs"):
                p = os.path.join(dp, fn)
                try:
                    yield p, io.open(p, encoding="utf-8", errors="replace").read()
                except OSError:
                    pass


def main():
    raw_parts, code_parts = [], []
    for _p, text in sources():
        raw_parts.append(text)
        code_parts.append(strip_comments(text))
    raw = "\n".join(raw_parts)
    code = "\n".join(code_parts)

    names = sorted({
        line.strip().split()[0]
        for line in io.open(os.path.join(ROOT, "docs", "baseline", "recovered_async_methods.txt"),
                            encoding="utf-8", errors="replace")
        if line.strip() and re.match(r"^[A-Za-z_]\w*$", line.strip().split()[0])
    })

    code_tokens = set(re.findall(r"\w+", code))
    raw_tokens = set(re.findall(r"\w+", raw))

    both, only_comment = [], []
    for n in names:
        async_n = n + "Async"
        in_code = n in code_tokens or async_n in code_tokens
        in_raw = n in raw_tokens or async_n in raw_tokens
        if in_code:
            both.append(n)
        elif in_raw:
            only_comment.append(n)

    total = len(names)
    print("names in the image: %d" % total)
    print("present in code:                    %4d  %.1f%%" % (len(both), 100.0 * len(both) / total))
    print("present only in comments:           %4d  %.1f%%" % (len(only_comment), 100.0 * len(only_comment) / total))
    print("absent from both:                   %4d  %.1f%%"
          % (total - len(both) - len(only_comment), 100.0 * (total - len(both) - len(only_comment)) / total))
    if only_comment:
        print("")
        print("the comment-only names:")
        for n in only_comment:
            print("  " + n)


if __name__ == "__main__":
    main()