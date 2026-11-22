"""C8's first run exposed its own classifier defects — fix them before trusting any number.

The report said `locale-key: 2851` and listed `AngleSharp.dll`, `RabbitMQ.Client`, `PubSub.dll`. Those are assembly
names, not resource keys: any dotted identifier matched. And `error-message: 4220` included "Microsoft Corporation. All
rights reserved" — dependency banners from libraries the image references and the replica does not.

So the classifier gains a `dependency` class and tighter rules. Without this the comparison answers the wrong question,
which is worse than not answering it.
"""
import io

PATH = 'analysis/c8_string_class_compare.py'
text = io.open(PATH, encoding='utf-8').read()

old_rules = '''URL = re.compile(r'^https?://\\S+$')
LOCALE_KEY = re.compile(r'^[A-Za-z][A-Za-z0-9]*(\\.[A-Za-z0-9_]+)+$')
SENTENCE = re.compile(r'^[A-Z][^\\n]{11,200}[.!?]$')


def classify(text):
    if URL.match(text):
        return 'url'
    if LOCALE_KEY.match(text) and ' ' not in text:
        return 'locale-key'
    if SENTENCE.match(text) and ' ' in text:
        return 'error-message'
    return 'other\''''

new_rules = '''URL = re.compile(r'^https?://\\S+$')
LOCALE_KEY = re.compile(r'^[A-Za-z][A-Za-z0-9_]*(\\.[A-Za-z][A-Za-z0-9_]*)+$')
SENTENCE = re.compile(r'^[A-Z][^\\n]{11,200}[.!?]$')
ASSEMBLY_FILE = re.compile(r'\\.(dll|exe|pdb|so|dylib)$', re.IGNORECASE)
BANNER = ('all rights reserved', 'ltd.', 'inc.', 'is the ultimate', 'a library for', 'implementation of',
          'open source', 'licenced', 'licensed under', 'copyright')


def classify(text):
    """Classify one string. Order matters: a url inside a banner is still a banner string's neighbour, not ours."""
    lowered = text.lower()

    if any(marker in lowered for marker in BANNER) or ASSEMBLY_FILE.search(text) or ', version=' in lowered:
        return 'dependency'

    if URL.match(text):
        return 'url'

    if ' ' not in text and len(text) <= 60 and LOCALE_KEY.match(text):
        return 'locale-key'

    if SENTENCE.match(text) and ' ' in text:
        return 'error-message'

    return 'other\''''

if old_rules not in text:
    raise SystemExit('rule block not found as written')
text = text.replace(old_rules, new_rules, 1)

text = text.replace(
    "    for kind in ('locale-key', 'url', 'error-message', 'other'):",
    "    for kind in ('locale-key', 'url', 'error-message', 'dependency', 'other'):")

text = text.replace(
    "    for kind in ('locale-key', 'url', 'error-message'):\n        samples = unknown_samples[kind]",
    "    for kind in ('locale-key', 'url', 'error-message'):\n        samples = unknown_samples[kind]")

io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('classifier tightened: dependency class added, assembly files excluded from locale keys')
