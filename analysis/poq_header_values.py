"""Print the full Poq header values, and locate poq-slot-conditions. (R778)

R777's reader truncates output for width; the poq-app-identifier is a GUID and needs all 36 characters. This also
looks for the one header name that was not in the request builder already decompiled.

Everything here goes through off_slot_reader's calibrated reader, so the layout assumptions are the ones R777 proved
rather than a second guess.
"""

import sys

sys.path.insert(0, r"D:\projects\cyber-reverse\analysis")
import off_slot_reader as osr  # noqa: E402

# name -> (header slot, value slot) as they appear in sub_140B3B7C0
PAIRS = [
    ("poq-country-identifier", 0x147115240, None),
    ("poq-app-id", 0x1471151D0, 0x146AE44D0),
    ("accept", 0x146F6C400, 0x146F76688),
    ("poq-app-identifier", 0x147115200, 0x146F65A48),
    ("authorization", 0x146F7CB78, 0x146B5C780),
    ("poq-currency-identifier", 0x147115288, None),
    ("version-code", 0x14717E5B8, 0x146AE3290),
    ("accept-language", 0x146F6C498, 0x147101D18),
    ("platform", 0x147113F48, 0x1470A7C68),
    ("poq-user-id", 0x147115310, None),
    ("accept-encoding", 0x146F6C460, 0x147044098),
    ("user-agent", 0x1471795D0, 0x146E46688),
]

# from R774's dump
SLOT_CONDITIONS_OBJECT = 0x1471152DC


def read(img, slot):
    for label, text, length in osr.interpretations(img, slot):
        if label == "object+12":
            return text, length
    return None, None


def main():
    img = osr.Image(osr.EXE)
    rule = osr.calibrate(img)
    if rule is None:
        print("\n  calibration failed; refusing to read anything else")
        return 1

    print("\n  %-24s %-22s %s" % ("header", "value", "length"))
    print("  " + "-" * 76)
    for name, hslot, vslot in PAIRS:
        h, _ = read(img, hslot)
        v, vl = read(img, vslot) if vslot else (None, None)
        shown = v if v is not None else "(not a constant here)"
        print("  %-24s %-22s %s" % (h or "?", shown, vl if vl is not None else ""))

    print("\n  poq-slot-conditions:")
    text, length = read(img, SLOT_CONDITIONS_OBJECT)
    print("    object 0x%x -> %r len=%s" % (SLOT_CONDITIONS_OBJECT, text, length))
    return 0


if __name__ == "__main__":
    sys.exit(main())
