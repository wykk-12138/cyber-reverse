"""Compute the ISO 3166-1 alpha-3 diff against the exported code list. (R680)

**Why this exists** (project convention §1.2): the IDA database cannot be opened this session (R636); the image side
comes from the R678 export, and the ISO side is `pycountry`, installed to the user site at R680 after R679 established
that the web could not supply an enumerable list.

**Why a local source**: R679's criterion referred to "the official 249" but the fetch truncated after seven entries, so
the criterion could not be evaluated -- not refuted, just unmeasurable. A criterion that names an external set is only
usable if that set is enumerable, so it is fetched offline instead.

**Criterion, unchanged from R679**: the difference is **exactly one element**, and the reverse difference is empty.
Anything else fails, and both sides are printed.
"""

import io
import json

import pycountry

IMAGE = r"D:\projects\cyber-reverse\analysis\country_codes.json"


def main():
    iso = {c.alpha_3 for c in pycountry.countries}
    image = set(json.load(io.open(IMAGE, encoding="utf-8")))

    print("ISO official     : %d" % len(iso))
    print("image (exported) : %d" % len(image))
    print()

    extra = sorted(image - iso)
    missing = sorted(iso - image)
    print("in image, not ISO : %d  %s" % (len(extra), extra if extra else "-"))
    print("in ISO, not image : %d  %s" % (len(missing), missing if missing else "-"))
    print()

    passed = len(extra) == 1 and not missing
    print("criterion 'difference is exactly one element': %s" % ("PASS" if passed else "FAIL"))
    print()

    for code in extra:
        rec = pycountry.countries.get(alpha_3=code)
        print("  extra %s -> %s" % (code, rec.name if rec else "(not in ISO at all)"))
    for code in missing:
        rec = pycountry.countries.get(alpha_3=code)
        print("  absent %s -> %s" % (code, rec.name if rec else "?"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
