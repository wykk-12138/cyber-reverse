"""R1282: one-pass teardown of the vendor-wiring ledger and the five caller-less islands.

Scope, decided by measurement rather than by guessing:
  * src/VendorWiring.cs                — ledger, 7 test files depend on it
  * VendorPaymentEndpoints / AccountRoutes / HbxApi / CheckoutRoutes / WaitwhileQueue — zero real callers in src
    (the three CheckoutRoutes hits in MagentoFlow are comments, verified line by line)

Everything here is either deletion or the removal of an assertion that read the table, a source file's prose, or both.
Behavioural assertions stay. Files are written as UTF-8 with LF; the previous round's PowerShell Set-Content is what
made four files invalid UTF-8.
"""
import io
import os
import re

SRC = 'src'
TST = 'tests/Cybersole.Tests'


def read(p):
    return io.open(p, encoding='utf-8').read()


def write(p, text):
    io.open(p, 'w', encoding='utf-8', newline='\n').write(text)


def drop(paths):
    for p in paths:
        if os.path.exists(p):
            os.remove(p)
            print('deleted', p)
        else:
            print('absent ', p)


def delete_method(path, name):
    """Remove a [Fact] method and the summary comment that belongs to it."""
    lines = read(path).split('\n')
    start = None
    for i, line in enumerate(lines):
        if re.search(r'public (?:async )?(?:void|Task) ' + re.escape(name) + r'\(', line):
            start = i
            break
    if start is None:
        print('  method not found:', name)
        return
    # walk back over attributes and the doc comment
    top = start
    while top > 0 and (lines[top - 1].strip().startswith('[') or lines[top - 1].strip().startswith('///')):
        top -= 1
    depth, end = 0, None
    started = False
    for i in range(start, len(lines)):
        depth += lines[i].count('{') - lines[i].count('}')
        if '{' in lines[i]:
            started = True
        if started and depth == 0:
            end = i
            break
    if end is None:
        print('  closing brace not found:', name)
        return
    # swallow a trailing blank line
    while end + 1 < len(lines) and lines[end + 1].strip() == '':
        end += 1
    del lines[top:end + 1]
    write(path, '\n'.join(lines))
    print('  removed method %s from %s' % (name, os.path.basename(path)))


def drop_line_block(path, first_line_marker, count):
    """Delete `count` lines starting at the first line containing the marker."""
    lines = read(path).split('\n')
    for i, line in enumerate(lines):
        if first_line_marker in line:
            del lines[i:i + count]
            write(path, '\n'.join(lines))
            print('  dropped %d lines at %s:%d' % (count, os.path.basename(path), i + 1))
            return
    print('  marker not found in %s: %s' % (os.path.basename(path), first_line_marker))


def replace_text(path, old, new):
    text = read(path)
    if old not in text:
        print('  text not found in %s' % os.path.basename(path))
        return
    write(path, text.replace(old, new))
    print('  rewrote text in', os.path.basename(path))


print('== delete the ledger, the five islands and the tests that exist only for them')
drop([
    os.path.join(SRC, 'Cybersole.Stores/Scripts/VendorWiring.cs'),
    os.path.join(SRC, 'Cybersole.Stores/Payments/VendorPaymentEndpoints.cs'),
    os.path.join(SRC, 'Cybersole.Stores/Flows/AccountRoutes.cs'),
    os.path.join(SRC, 'Cybersole.Stores/Flows/HbxApi.cs'),
    os.path.join(SRC, 'Cybersole.Stores/Flows/CheckoutRoutes.cs'),
    os.path.join(SRC, 'Cybersole.Stores/WaitwhileQueue.cs'),
    os.path.join(TST, 'VendorWiringTests.cs'),
    os.path.join(TST, 'VendorPaymentEndpointTests.cs'),
    os.path.join(TST, 'AccountRoutesTests.cs'),
    os.path.join(TST, 'HbxApiTests.cs'),
    os.path.join(TST, 'CheckoutRoutesTests.cs'),
    os.path.join(TST, 'WaitwhileQueueTests.cs'),
])

print('== detach the remaining references')
# real dependencies on the table
drop_line_block(os.path.join(TST, 'WallDispatchTests.cs'),
                'Assert.Equal(new[] { "cloudflare", "kasada", "datadome" }', 3)
drop_line_block(os.path.join(TST, 'WallSolvingTests.cs'),
                'Assert.Equal(VendorWiring.State.Wired, VendorWiring.For("datadome")', 1)
drop_line_block(os.path.join(TST, 'WallSolvingTests.cs'),
                'Assert.Equal(VendorWiring.State.DetectedOnly, VendorWiring.For("queue-it")', 1)

# prose that named the table
replace_text(os.path.join(TST, 'AntiBotProtocolTests.cs'),
             '// the third copy of that false absence: the doc comment, VendorWiring',
             '// the false absence that used to be recorded three times over')
replace_text(os.path.join(TST, 'PerimeterXMarkerTests.cs'),
             'and not <see cref="VendorWiring.Gap.VendorAbsent"/>',
             'and not the "vendor absent" kind (docs/VENDOR_WIRING.md §10)')
replace_text(os.path.join(TST, 'PerimeterXMarkerTests.cs'),
             'the two assertions that used to sit here read VendorWiring.R',
             'the two assertions that used to sit here read the audit table\'s R')

# assertions that read another test file's text
drop_line_block(os.path.join(TST, 'VendorNegativeClaimsTests.cs'),
                '"tests", "Cybersole.Tests", "VendorWiringTests.cs"', 5)
delete_method(os.path.join(TST, 'VendorNegativeClaimsTests.cs'), 'TheClaimCarriesItsEvidence')
drop_line_block(os.path.join(TST, 'CaptchaDeliveryAttributionTests.cs'),
                '"src", "Cybersole.Stores", "Scripts", "VendorWiring.cs"', 4)

# Casio's checkout-route test asserted against the archived constants
delete_method(os.path.join(TST, 'CasioEndpointTests.cs'), 'TheCheckoutRoutesAreWhereTheFlowThinksTheyAre')
print('done')
