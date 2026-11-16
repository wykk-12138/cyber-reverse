"""Classify the myshopify slugs: random-id hosts versus readable store names. (R814, rule corrected)

The first rule called 19dd5a-be readable because its tail segment is only two characters and so escaped the hex test.
A suffix like -be or -49 is part of the random pattern, not a word, so the rule now asks whether any segment is a real
word: three or more letters, containing a vowel, and not pure hexadecimal. Stating the rule plainly matters more than
making it clever, because this produces a count rather than a verdict.
"""

import io
import re
import subprocess
import sys

ROOT = r"D:\projects\cyber-reverse"
POOL = ROOT + r"\analysis\pe_strings.txt"
CATALOG = ROOT + r"\analysis\store_catalog.py"

low = io.open(POOL, encoding="utf-8", errors="replace").read().lower()
slugs = sorted(set(re.findall(r"([a-z0-9][a-z0-9\-]{1,40})\.myshopify\.com", low)))

HEX = re.compile(r"^[0-9a-f]+$")
VOWELS = set("aeiou")


def is_word(seg):
    if len(seg) < 3:
        return False
    if not (set(seg) & VOWELS):
        return False
    if HEX.match(seg):
        return False
    return True


def looks_random(slug):
    return not any(is_word(p) for p in slug.split("-") if p)


random_ids = [s for s in slugs if looks_random(s)]
readable = [s for s in slugs if not looks_random(s)]

print("  distinct myshopify slugs: %d" % len(slugs))
print("  random-id shaped:         %d" % len(random_ids))
print("  readable-shaped:          %d" % len(readable))
print()
print("  every readable slug:")
for i, s in enumerate(readable, 1):
    print("    %3d  %s" % (i, s))

res = subprocess.run([sys.executable, CATALOG], capture_output=True, text=True)
covered = set(re.findall(r"\b([a-z0-9\-]+)\.(?:com|co\.uk|nl|ca|eu|app|io|net|de|fr)\b",
                         res.stdout.lower()))

def matched(slug):
    for c in covered:
        if slug.startswith(c) or c.startswith(slug):
            return c
    return None

hit = [(s, matched(s)) for s in readable if matched(s)]
miss = [s for s in readable if not matched(s)]

print()
print("  readable slugs matched to a replica domain: %d" % len(hit))
for s, c in hit:
    print("    %-30s ~ %s" % (s, c))
print()
print("  readable slugs with no replica counterpart: %d" % len(miss))
