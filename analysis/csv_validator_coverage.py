"""How complete is the replica's profile-CSV validator? (R592)

`docs/COPY_QUEUE.md` flags two strings the replica never uses:

    ProfileCsv.Error.UnknownCountry   Unknown country "{0}"
    ProfileCsv.Error.UnknownState     Unknown state "{0}" for {1}

That implies the original's CSV validator rejects a profile whose country or state it does not recognise. This counts
the whole `ProfileCsv.Error.*` family in the locale table (the authoritative list of what the original reports) and
checks which of those the replica's source actually references, so the incompleteness is a number rather than an
impression.

It also confirms whether the replica holds any country/state data to validate against — without that, adding the two
checks would mean inventing the table, not implementing the behaviour.

Read-only.
"""

import glob
import io
import json
import os
import re

REPO = r"D:\projects\cyber-reverse\replica"
LOCALE = os.path.join(REPO, "src", "Cybersole.Core", "Locales", "Cybersole.Locales.en.json")
SRC = os.path.join(REPO, "src")

# names that would appear in a real country/state table
STATE_PROBES = ["Alabama", "California", "Ontario", "Queensland", "Bavaria", "New York"]


def source_blob():
    parts = []
    for path in glob.glob(os.path.join(SRC, "**", "*.cs"), recursive=True):
        if os.sep + "obj" in path or os.sep + "bin" in path:
            continue
        parts.append(io.open(path, encoding="utf-8", errors="replace").read())
    return "\n".join(parts)


def main():
    locale = json.load(io.open(LOCALE, encoding="utf-8"))
    family = {k: v for k, v in locale.items() if k.startswith("ProfileCsv.Error.")}

    blob = source_blob()
    print("locale keys in ProfileCsv.Error.* : %d" % len(family))
    print()
    print("%-38s %-14s %s" % ("key", "referenced?", "value"))
    print("-" * 100)

    used, unused = [], []
    for k in sorted(family):
        v = family[k]
        # the replica writes these as `["ErrorXxx"] = "…"   // ProfileCsv.Error.Xxx`
        referenced = k in blob
        (used if referenced else unused).append(k)
        print("%-38s %-14s %s" % (k, "yes" if referenced else "NO", v[:44]))

    print()
    print("referenced : %d" % len(used))
    print("unreferenced: %d  -> %s" % (len(unused), ", ".join(k.split(".")[-1] for k in unused)))

    print()
    found = [p for p in STATE_PROBES if p in blob]
    print("country/state data present in src/: %s" % (found or "NONE"))
    print("  (a validator needs a country -> states table; store-flow country lists are not it)")


if __name__ == "__main__":
    main()
