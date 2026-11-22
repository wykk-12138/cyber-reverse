"""C8: compare the two string pools class by class — locale keys, urls, error messages.

docs/PARITY_CLAIMS.md lists C8 as unknown because no tool does this: `analysis/pe_strings.txt` holds the image's pool and
the replica's AOT artifact holds its own, but nothing splits them into the three classes and compares each one.

Two rules from this project decide the shape of the answer:

  * §4.5 — a string absent from the AOT artifact carries no information, because NativeAOT stores some literals in
    forms a byte scan cannot see. So "in the image, not in the artifact" is reported as **unknown**, never as missing.
  * R816 — a pool is not necessarily complete. The image side is IDA's own string list (324,901 entries), which is the
    closest thing to complete this project has; the artifact side is a byte scan of the published exe.

What it therefore reports: how many strings of each class each side has, how many the artifact certainly covers
(exact text present), and a sample of the unknown remainder. That is a comparison, not a verdict on parity.

Usage:
    python analysis/c8_string_class_compare.py               # summary
    python analysis/c8_string_class_compare.py --write-doc   # refresh docs/C8_STRING_CLASSES.md
"""
import argparse
import collections
import io
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

IMAGE_POOL = 'analysis/ida_strings.txt'
ARTIFACT = 'replica/.publish-aot/Cybersole.Ui.exe'
DOC = 'docs/C8_STRING_CLASSES.md'

URL = re.compile(r'^https?://\S+$')
LOCALE_KEY = re.compile(r'^[A-Za-z][A-Za-z0-9_]*(\.[A-Za-z][A-Za-z0-9_]*)+$')
SENTENCE = re.compile(r'^[A-Z][^\n]{11,200}[.!?]$')
ASSEMBLY_FILE = re.compile(r'\.(dll|exe|pdb|so|dylib)$', re.IGNORECASE)
BANNER = ('all rights reserved', 'ltd.', 'inc.', 'is the ultimate', 'a library for', 'library for',
          'implementation of', 'open source', 'licenced', 'licensed under', 'copyright',
          'provides ', 'abstractions', 'provider for', 'wrapper for', 'binding for', 'runtime library',
          'strongly typed', 'key-value pair')

# An assembly name looks like Dotted.Title.Case and never has a lowercase-only segment; a resource key usually does.
ASSEMBLY_NAME = re.compile(r'^([A-Z][A-Za-z0-9]+\.)+[A-Z][A-Za-z0-9]+$')


def classify(text):
    """Classify one string. Order matters: a url inside a banner is still a banner string's neighbour, not ours."""
    lowered = text.lower()

    if (any(marker in lowered for marker in BANNER) or ASSEMBLY_FILE.search(text)
            or ', version=' in lowered or ASSEMBLY_NAME.match(text)):
        return 'dependency'

    if URL.match(text):
        return 'url'

    if ' ' not in text and len(text) <= 60 and LOCALE_KEY.match(text):
        return 'locale-key'

    if SENTENCE.match(text) and ' ' in text:
        return 'error-message'

    return 'other'


def image_strings(limit=None):
    seen = {}
    for line in io.open(IMAGE_POOL, encoding='utf-8', errors='replace'):
        parts = line.rstrip('\n').split('\t', 1)
        if len(parts) != 2:
            continue
        text = parts[1].strip()
        if 6 <= len(text) <= 400 and text not in seen:
            seen[text] = parts[0]
        if limit and len(seen) >= limit:
            break
    return seen


def artifact_strings(path):
    data = io.open(path, 'rb').read()
    found = set()

    for match in re.finditer(rb'[\x20-\x7e]{6,400}', data):
        found.add(match.group(0).decode('ascii', errors='ignore'))

    for match in re.finditer(rb'(?:[\x20-\x7e]\x00){6,400}', data):
        found.add(match.group(0).decode('utf-16-le', errors='ignore'))

    return found


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-doc', action='store_true')
    arguments = parser.parse_args()

    image = image_strings()
    artifact = artifact_strings(ARTIFACT)

    image_classes = collections.Counter()
    artifact_classes = collections.Counter()
    coverage = collections.Counter()
    unknown_samples = collections.defaultdict(list)

    for text in image:
        kind = classify(text)
        image_classes[kind] += 1
        if text in artifact:
            coverage[kind] += 1
        elif kind != 'other' and len(unknown_samples[kind]) < 12:
            unknown_samples[kind].append(text)

    for text in artifact:
        artifact_classes[classify(text)] += 1

    lines = []
    lines.append('image strings: %d   artifact strings: %d' % (len(image), len(artifact)))
    lines.append('')
    lines.append('%-15s %9s %9s %9s' % ('class', 'image', 'artifact', 'exact-in-artifact'))
    for kind in ('locale-key', 'url', 'error-message', 'dependency', 'other'):
        lines.append('%-15s %9d %9d %9d' % (kind, image_classes[kind], artifact_classes[kind], coverage[kind]))
    lines.append('')
    lines.append('unknown (in the image, not found in the artifact — §4.5 says this means nothing yet):')
    for kind in ('locale-key', 'url', 'error-message'):
        samples = unknown_samples[kind]
        lines.append('  %s: %d unknown; samples: %s' % (kind, image_classes[kind] - coverage[kind],
                                                        ' | '.join(s[:40] for s in samples[:6])))
    lines.append('')
    lines.append('Limits, stated rather than papered over:')
    lines.append('  1. the artifact side is a byte scan, and NativeAOT stores some literals in forms a scan cannot')
    lines.append('     see, so "in the image, not in the artifact" is unknown, never missing (§4.5);')
    lines.append('  2. the image pool carries referenced-assembly metadata — assembly names and NuGet')
    lines.append('     descriptions — which no text rule separates perfectly, so these counts are upper bounds;')
    lines.append('  3. the image side is IDA\'s own list, and it concatenates adjacent strings into one entry —')
    lines.append('     samples like "Bogus.dllg" are two strings run together — which inflates the dotted classes;')
    lines.append('  4. this answers "what is comparable", not "what matches": it is a comparison instrument,')
    lines.append('     not a verdict on parity.')

    report = '\n'.join(lines)
    print(report)

    if arguments.write_doc:
        io.open(DOC, 'w', encoding='utf-8', newline='').write(
            '# C8 字符串池分类比对（生成物）\n\n```\n' + report + '\n```\n')
        print('\nwrote %s' % DOC)

    return 0


if __name__ == '__main__':
    sys.exit(main())
