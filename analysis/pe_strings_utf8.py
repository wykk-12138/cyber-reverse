"""Extract UTF-8 strings INCLUDING multi-byte — the thing `pe_strings.py` cannot do. (R669)

**Why this exists** (project convention §1.2): the IDA database cannot be opened this session (R636), and the public
tools in `seep-reverse-lab` / `rea` do not ship a "dump the UTF-8 string pool with CJK" utility; `pe_strings.py` is the
in-repo extractor, and R668 measured that it loses every non-ASCII byte.

**Why it is a separate file and not an edit**: `analysis/pe_strings.txt` is the baseline that a dozen conclusions cite.
Replacing it silently would mean those conclusions were validated against a different pool than they claim. So this
writes a **second** file, and the delta between the two is the measurement.

**What `pe_strings.py` does wrong, exactly**:

  * `utf16_runs` accepts a code unit only when the high byte is 0 and the low byte is printable ASCII. A CJK character
    in UTF-16LE has a non-zero high byte, so it **terminates** the run.
  * `utf8_runs` is the regex `[\\x20-\\x7e]{6,}` -- printable ASCII only. Every multi-byte UTF-8 sequence is a
    terminator.

Both therefore cut the Japanese and Chinese locale blobs into ASCII fragments, which is why
`"ProfileCsv.Error.UnknownCountry": "` appeared "truncated" at R668.

This extractor runs the regex `[utf8 lead][utf8 continuation]+` over the file and decodes as UTF-8, keeping runs whose
characters are printable (no control characters).

Usage:
    python pe_strings_utf8.py <exe> <out.txt> [min_chars]
"""

import io
import re
import sys

# A UTF-8 sequence: 1-byte ASCII, or 2-4 bytes with continuation bytes. Runs of at least `min_chars` characters.
RUN = re.compile(
    rb"(?:[\x20-\x7e]|[\xc2-\xdf][\x80-\xbf]|[\xe0-\xef][\x80-\xbf]{2}|[\xf0-\xf4][\x80-\xbf]{3}){%d,}"
)


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2

    path, out_path = sys.argv[1], sys.argv[2]
    min_chars = int(sys.argv[3]) if len(sys.argv) > 3 else 6

    data = io.open(path, "rb").read()
    print("read %d bytes from %s" % (len(data), path))

    pattern = re.compile(RUN.pattern.replace(b"{%d,}", b"{%d,}" % min_chars))
    seen = set()
    lines = []
    dropped = 0
    for m in pattern.finditer(data):
        raw = m.group()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            dropped += 1
            continue
        if text in seen:
            continue
        seen.add(text)
        lines.append("0x%08x  %s" % (m.start(), text))

    print("distinct strings: %d  (undecodable runs dropped: %d)" % (len(lines), dropped))
    io.open(out_path, "w", encoding="utf-8", newline="").write("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
