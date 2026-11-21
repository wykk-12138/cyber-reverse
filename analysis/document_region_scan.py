"""Walk the document region and read every GraphQL operation it holds.

`ida.py str` returned seven operations while the replica carries twenty, so it is not an enumeration of the
document pool — it is a search over whatever IDA calls a string, which excludes the long ones. Using it for a set
difference would have produced a confident, wrong answer, which is exactly the §2.7b failure mode.

This walks the region the documents live in — the decoded ones have all come from 0x1470C0000..0x147150000 — and
tests every four-byte boundary for a frozen string header: a MethodTable pointer, a length, and characters that
begin an operation. Nothing is assumed about how the pool is ordered; the scan just reads what is there.

Usage: python analysis/document_region_scan.py
"""
import io
import json
import os
import re
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

START = 0x1470C0000
END = 0x147150000
METHOD_TABLE = 0x144DB6A40
PATTERN = re.compile(r'(?:mutation|query)\s+(\w+)\s*[\(\{]')


def bytes_at(address, size):
    """Read bytes. The reply arrives as a list, or as a JSON string wrapping one under "result"."""
    reply = call('get_bytes', {'regions': [{'addr': hex(address), 'size': size}]})
    if isinstance(reply, str):
        try:
            reply = json.loads(reply)
        except json.JSONDecodeError:
            # Two JSON objects on one line: the tool prefixes a status object. Take the one with a region.
            for line in reply.splitlines():
                for candidate in (line, line[line.find('{'):]):
                    try:
                        parsed = json.loads(candidate)
                    except json.JSONDecodeError:
                        continue
                    body = parsed.get('result', parsed) if isinstance(parsed, dict) else parsed
                    if isinstance(body, list) and body and 'data' in body[0]:
                        reply = body
                        break
                if not isinstance(reply, str):
                    break
        if isinstance(reply, str):
            raise RuntimeError('unreadable get_bytes reply: %s' % reply[:120])
    if isinstance(reply, dict):
        reply = reply.get('result', reply)
    region = reply[0] if isinstance(reply, list) else reply
    data = region['data']
    if isinstance(data, str):
        text = data[2:] if data.startswith('0x') else data
        return bytes(int(part, 16) for part in text.split())
    return bytes(data)


found = {}
offset = START
while offset < END:
    want = min(8192, END - offset)      # 64 KiB replies come back abbreviated with an ellipsis
    chunk = bytes_at(offset, want)

    for index in range(0, len(chunk) - 16, 4):
        table = int.from_bytes(chunk[index:index + 8], 'little')
        if table != METHOD_TABLE:
            continue
        length = int.from_bytes(chunk[index + 8:index + 12], 'little')
        if not 40 <= length <= 40000:
            continue

        head = chunk[index + 12:index + 12 + 96]
        if len(head) < 2:
            continue
        text = head.decode('utf-16-le', errors='replace')
        match = PATTERN.match(text)
        if not match:
            continue

        found[match.group(1)] = (offset + index + 12, length)

    offset += want

print('operations found in the region: %d' % len(found))
for name in sorted(found):
    address, length = found[name]
    print('   %-44s %#x  %d chars' % (name, address, length))

with io.open('analysis/.operations_in_image.json', 'w', encoding='utf-8', newline='') as handle:
    json.dump({name: {'addr': address, 'length': length} for name, (address, length) in found.items()},
              handle, indent=1, sort_keys=True)
print('wrote analysis/.operations_in_image.json')
