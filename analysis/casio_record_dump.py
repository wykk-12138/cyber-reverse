"""Dump the Casio configuration record as text, to find the region token. (R786)

R785 established that four pieces of Casio work -- login, registration, cart, payment -- are all blocked on the same
missing thing: the region token and how it is spelled in the /{region}/ prefix. The Casio field names live in a
contiguous block around 0x146fc1d94 (casio.com), which is where the record's packed key/value pairs sit. Dumping that
window as text is more direct than searching for guesses about what the token might be called.

Reads through off_slot_reader's Image, so the section map and VA-to-file conversion are the ones already checked.
"""

import sys

sys.path.insert(0, r"D:\projects\cyber-reverse\analysis")
import off_slot_reader as osr  # noqa: E402

# the block holding casio.com, the five casio_ fields and casioid
START = 0x146B7D800
END = 0x146B7FA00


def printable_runs(text):
    """Split on control characters, keeping offsets so a hit can be traced back."""
    runs = []
    cur = []
    start = 0
    for i, ch in enumerate(text):
        if 0x20 <= ord(ch) <= 0x7E:
            if not cur:
                start = i
            cur.append(ch)
        else:
            if len(cur) >= 3:
                runs.append((start, "".join(cur)))
            cur = []
    if len(cur) >= 3:
        runs.append((start, "".join(cur)))
    return runs


def main():
    img = osr.Image(osr.EXE)
    if START < osr.IMAGE_BASE:
        print('  START 0x%x is below the image base 0x%x -- the literal lost a digit' % (START, osr.IMAGE_BASE))
        return 2
    off = img.file_offset(START)
    if off is None:
        print("  start address is not file-backed")
        return 1
    raw = img.data[off:off + (END - START)]
    text = raw.decode("utf-16-le", "replace")

    print("  window 0x%x..0x%x  (%d bytes, file 0x%x)" % (START, END, len(raw), off))
    print()
    for rel, run in printable_runs(text):
        print("    +0x%04x  0x%09x  %r" % (rel, START + rel, run))
    return 0


if __name__ == "__main__":
    sys.exit(main())
