"""Check whether the hand-written TLS stack reaches more than one real host. (R818)

The pinned-defect test reports HTTP 200 from nike.com through the replica's own TLS 1.2 implementation, while its doc
comment still says nike.com returns bad_record_mac and that the browser path is the only way to reach a real store.
One host could be luck; this asks for several, so the claim that replaces the comment is grounded.

Uses the replica's own NetClient through the test assembly rather than a new client, because the question is about that
client and nothing else.
"""

import io
import re

TESTS = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\TlsTransportPerformanceTests.cs"

t = io.open(TESTS, encoding="utf-8", errors="replace").read()
m = re.search(r'Url\s*=\s*"([^"]+)"', t)
print("  the test's Url: %s" % (m.group(1) if m else "(not found as a literal)"))

i = t.find("bad_record_mac")
print()
print("  the stale comment in full:")
start = t.rfind("/// <summary>", 0, i)
end = t.find("[Fact]", i)
for line in t[start:end].splitlines():
    print("    " + line.strip()[:108])

print()
print("  what the test actually asserts about the outcome:")
j = t.find("TheOwnTlsDefectIsPinned")
seg = t[j:j + 1400]
for line in seg.splitlines():
    s = line.strip()
    if s.startswith("Assert") or s.startswith("//"):
        print("    " + s[:104])
