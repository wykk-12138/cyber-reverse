"""Gate the two device prunes on the Apple profile, as R193 already does for its own bodies. (R819)

GlobalPrune deletes every window name the device's own list does not carry. The list is the iPhone's -- 1062 names from
Object.getOwnPropertyNames(window) on a captured device, per WindowNameTable -- so applying it to a desktop profile
deletes desktop-only names, and window.chrome is one of them.

ChromiumStealthTests.TheRestOfTheFingerprintLooksOrdinary measures exactly this and reports
{"chrome":"undefined","runtime":"undefined", ...} while every other property in the same probe is correct: five plugins,
en-US,en, eight cores, eight gigabytes, "Intel Inc." and UA-CH brands without Headless. The test is excluded from the
default suite because it drives a real browser, which is why the defect survived.

ChromiumBridge already gates every other body that asserts iPhone facts on MobileSurface.IsAppleUserAgent -- the comment
at line 344 says a desktop profile must not inherit iPhone-only globals. These two prunes never got that gate.

The change keeps the ordering the comments require (after WindowOrderWrap, before CssStyleProperties) by wrapping only
those two appends.
"""

import io

PATH = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\ChromiumBridge.cs"

OLD = """        surfaceBody += GlobalPrune.GlobalBodyJs();
        surfaceBody += GlobalPrune.DocumentBodyJs();
"""

NEW = """        // R819: gated on the device claim, like every other body that asserts iPhone facts (R193 states the rule
        // two blocks below: a desktop profile must not inherit iPhone-only globals). Both prunes delete every window
        // name the device's list does not carry, and that list is the captured iPhone's 1062 names -- so running them
        // for a desktop profile removed `chrome`, which a desktop Chrome reports as an object. Measured by
        // ChromiumStealthTests.TheRestOfTheFingerprintLooksOrdinary: every other property in its probe was correct
        // while chrome came back undefined. That test drives a real browser and is excluded from the default suite,
        // which is why the deletion stayed invisible.
        if (MobileSurface.IsAppleUserAgent(userAgent))
        {
            surfaceBody += GlobalPrune.GlobalBodyJs();
            surfaceBody += GlobalPrune.DocumentBodyJs();
        }
"""


def main():
    t = io.open(PATH, encoding="utf-8").read()
    n = t.count(OLD)
    if n != 1:
        print("  anchor appears %d times — refusing to write" % n)
        return 1
    out = t.replace(OLD, NEW, 1)

    # guards
    if "R819: gated on the device claim" not in out:
        print("  marker missing after replace — refusing")
        return 1
    if out.count("GlobalPrune.GlobalBodyJs()") != 1:
        print("  unexpected count of GlobalBodyJs — refusing")
        return 1
    io.open(PATH, "w", encoding="utf-8", newline="").write(out)
    print("  gated both prunes on MobileSurface.IsAppleUserAgent")
    print("  GlobalBodyJs occurrences: %d" % out.count("GlobalPrune.GlobalBodyJs()"))
    print("  DocumentBodyJs occurrences: %d" % out.count("GlobalPrune.DocumentBodyJs()"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
