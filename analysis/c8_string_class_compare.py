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
UI_LOCALE_KEY = re.compile(
    r'^(?:AccountSelectionMode|Accounts|AccountsCreator|ActionsModal|Advanced|Analytics|Auth|'
    r'Browser|CaptchaSource|Cart|Checkout|CloudflareSolver|Common|CreateGroup|Creator|Data|Empty|'
    r'ExceedBehaviour|ExpressionView|GroupModal|HistoryWindow|KeyBinds|Language|Modal|Monitor|'
    r'MonitorMode|Nav|Notifications|ProfileAddress|ProfileAdvanced|ProfileCreator|ProfileCsv|'
    r'ProfilePayment|Profiles|Proxies|ProxyCreator|ProxyGroup|ProxyTester|PublishTemplate|'
    r'QueuePresentation|Release|Settings|SmartActionSettings|SmartActions|SmartActionsCreator|'
    r'Solver|StaggerStart|TaskCreator|TaskDetails|TaskGroup|TaskGroups|Tasks|TemplateView|'
    r'TimeAgo|TimeRelative|Update|User|Utilities)'
    r'(?:\.[A-Za-z0-9-]+)+$'
)
LOCALE_KEY = re.compile(r'^[A-Z][a-z][A-Za-z0-9]{1,}(\.[A-Z][A-Za-z0-9]{1,})+$')
SENTENCE = re.compile(r'^[A-Z][^\n]{11,200}[.!?]$')
ASSEMBLY_FILE = re.compile(
    r'(?:^|[A-Za-z0-9_])\.(?:[dD][lL]{2}|[eE][xX][eE]|[pP][dD][bB]|[dD][yY][lL][iI][bB])(?:$|[0-9A-Za-z_.])'
    r'|\.[sS][oO](?:$|[^a-z])'
)
FRAMEWORK_DOTTED = re.compile(
    r'^[A-Za-z0-9]?(?:System|Microsoft|Avalonia|SkiaSharp|BouncyCastle|MailKit|MimeKit|Newtonsoft|'
    r'Polly|Grpc|Google|AngleSharp|Sentry|Serilog|OpenTelemetry|DnsClient|Bogus|K4os|ZstdSharp|'
    r'LibTessDotNet|HarfBuzzSharp|SixLabors|Tmds|Acornima|Jint|Esprima|CommunityToolkit)\.',
    re.ASCII,
)
REFLECTION_OR_ENUM_DOTTED = re.compile(
    r'(?:^|\.)(?:get_|set_|add_|remove_|WM_|I[A-Z][a-z])|^[A-Z][A-Z0-9_]{3,}(?:\.[A-Z0-9_]{3,})+$'
)
DOMAIN_OR_MINIFIED_DOTTED = re.compile(
    r'^(?:[a-z0-9-]+\.)+(?:com|net|org|io|co|za|az|uk|de|jp|fr|cloud|dev|app)$'
    r'|^[A-Za-z0-9]{1,5}\.[a-z][A-Za-z0-9]{0,3}$',
    re.IGNORECASE,
)
DEP_URL_MARKERS = (
    'ocsp.', '.crl', '/crl', 'dpcs/', '/cps', 'cacerts', '/pki', 'crl.', 'aia.',
    'schemas.microsoft.com', 'schemas.xmlsoap.org', 'schemas.openxmlformats.org',
    'www.w3.org', 'www.ibm.com/data/dtd', 'purl.org', 'apache.org', 'opensource.org',
    'github.com/', 'james.newtonking.com', 'icsharpcode.net', 'aka.ms/',
    'typography.com/support/eula', 'microsoft.com/wsdl',
)
BANNER = (
    'all rights reserved', 'ltd.', 'inc.', 'is the ultimate', 'a library for', 'library for',
    'implementation of', 'open source', 'licenced', 'licensed under', 'copyright',
    'provides ', 'abstractions', 'provider for', 'wrapper for', 'binding for', 'runtime library',
    'strongly typed', 'key-value pair',
    'is a cross-platform', 'is obsolete', 'has been deprecated', 'should not be used',
    'experimentalesfeatures', 'for .net', 'relies on dynamically', 'going away in a future version',
    'file system globbing', 'logging infrastructure', 'bindingexpression', 'reflectionbinding',
    'was renamed to', 'instead.', 'live request stream from an application', 'request bodies (',
    'see https://aka.ms/', 'validation_err', 'security_err', 'network_err', 'syntax_err',
    'namespace_err', 'invalid_access_err', 'type_mismatch_err', 'abort_err',
    'arrays of reference types', 'is in preview and subject to', 'uses reflection to',
    'supplied node is incorrect', 'the api will return', 'not in the allowed range',
)

# An assembly name looks like Dotted.Title.Case and never has a lowercase-only segment; a resource key usually does.
ASSEMBLY_NAME = re.compile(r'^([A-Z][A-Za-z0-9]+\.)+[A-Z][A-Za-z0-9]+$')


def classify(text):
    """Classify one string. Order matters: dependency/metadata noise is separated before URL/locale/message."""
    lowered = text.lower()
    is_url = bool(URL.match(text))

    if (any(marker in lowered for marker in BANNER)
            or (not is_url and ASSEMBLY_FILE.search(text))
            or ', version=' in lowered
            or FRAMEWORK_DOTTED.match(text)):
        return 'dependency'

    if ' ' not in text and len(text) <= 60 and UI_LOCALE_KEY.match(text):
        return 'locale-key'

    if ASSEMBLY_NAME.match(text):
        return 'dependency'

    if is_url:
        if any(marker in lowered for marker in DEP_URL_MARKERS):
            return 'dependency'
        return 'url'

    if ' ' not in text and len(text) <= 60 and LOCALE_KEY.match(text):
        if REFLECTION_OR_ENUM_DOTTED.search(text):
            return 'dependency'
        if DOMAIN_OR_MINIFIED_DOTTED.match(text):
            return 'other'
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
