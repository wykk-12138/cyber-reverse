"""One more pass on C8's classifier, then accept its limit and say so.

Second run still listed `RabbitMQ.Client` as a locale key and `C# runtime library for Protocol Buffers` as an error
message. Both are referenced-assembly metadata: the image's pool carries the assembly names and NuGet descriptions of
everything it links. A text-only classifier can narrow that, not eliminate it — so this adds the markers and the
assembly-name shape, and then the report states the residual limitation instead of implying precision it does not have.
"""
import io

PATH = 'analysis/c8_string_class_compare.py'
text = io.open(PATH, encoding='utf-8').read()

old = """BANNER = ('all rights reserved', 'ltd.', 'inc.', 'is the ultimate', 'a library for', 'implementation of',
          'open source', 'licenced', 'licensed under', 'copyright')"""
new = """BANNER = ('all rights reserved', 'ltd.', 'inc.', 'is the ultimate', 'a library for', 'library for',
          'implementation of', 'open source', 'licenced', 'licensed under', 'copyright',
          'provides ', 'abstractions', 'provider for', 'wrapper for', 'binding for', 'runtime library',
          'strongly typed', 'key-value pair')

# An assembly name looks like Dotted.Title.Case and never has a lowercase-only segment; a resource key usually does.
ASSEMBLY_NAME = re.compile(r'^([A-Z][A-Za-z0-9]+\\.)+[A-Z][A-Za-z0-9]+$')"""
if old not in text:
    raise SystemExit('banner block not found')
text = text.replace(old, new, 1)

text = text.replace(
    "    if any(marker in lowered for marker in BANNER) or ASSEMBLY_FILE.search(text) or ', version=' in lowered:",
    "    if (any(marker in lowered for marker in BANNER) or ASSEMBLY_FILE.search(text)\n"
    "            or ', version=' in lowered or ASSEMBLY_NAME.match(text)):")

text = text.replace(
    "    lines.append('not a parity verdict: the artifact side is a byte scan, and NativeAOT stores some literals in forms')\n"
    "    lines.append('a scan cannot see. A count here answers \"what is comparable\", not \"what matches\".')",
    "    lines.append('Limits, stated rather than papered over:')\n"
    "    lines.append('  1. the artifact side is a byte scan, and NativeAOT stores some literals in forms a scan cannot')\n"
    "    lines.append('     see, so \"in the image, not in the artifact\" is unknown, never missing (§4.5);')\n"
    "    lines.append('  2. the image pool carries referenced-assembly metadata — assembly names and NuGet')\n"
    "    lines.append('     descriptions — which no text rule separates perfectly, so these counts are upper bounds;')\n"
    "    lines.append('  3. this answers \"what is comparable\", not \"what matches\": it is a comparison instrument,')\n"
    "    lines.append('     not a verdict on parity.')")

io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('markers, assembly-name rule and the limits block added')
