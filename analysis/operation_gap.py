"""Compare the complete operation inventory with what the replica carries AND what production flows invoke.

R1382 honesty update: scanning replica/src for `(mutation|query) <Name>` proves only that the GraphQL text
exists as a constant in source ("declared"). Many operations live only inside a `DocumentFor` switch in their
own `*Queries.cs` file with zero external callers, and many wired branches sit behind `Session.Vars` trigger
keys that zero production code ever writes ("side-door"). This reports all three layers so text presence
cannot be misread as runtime checkout parity.

Usage: python analysis/operation_gap.py
"""
import io
import json
import os
import re

ROOT = 'replica/src'
PATTERN = re.compile(r'(?:mutation|query)\s+(\w+)\s*[\(\{]')
SIDE_DOOR_PREFIXES = (
    'ao.contactBody', 'braintree.', 'checkout.orderId', 'checkout.origin',
    'cybersource.', 'graphqlHash.', 'onRunning.', 'paypal.browserEuat',
    'paypal.clientMetadataId', 'paypal.conversionType', 'paypal.partnerToken',
    'paypal3ds.providerFields', 'productdrops.', 'saucony.threeDsReply',
    'shopapp.', 'storeSession.', 'storefrontapi.', 'themeapis.',
    'wh.onboard.', 'casio.sku',
)

image = json.loads(io.open('analysis/.operations_in_image.json', encoding='utf-8').read())

all_src = {}
replica = {}
def_files = {}
for base, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in ('bin', 'obj')]
    for name in files:
        if not name.endswith('.cs'):
            continue
        path = os.path.join(base, name)
        rel = os.path.relpath(path, ROOT)
        text = io.open(path, encoding='utf-8', errors='replace').read()
        all_src[rel] = text
        for found in PATTERN.finditer(text):
            op = found.group(1)
            replica.setdefault(op, rel)
            def_files.setdefault(op, set()).add(rel)

covered = sorted(set(image) & set(replica))
missing = sorted(set(image) - set(replica), key=lambda name: -image[name]['length'])

# Layer 2: accurately classify whether each image operation is actually invoked from a production flow/gateway
# outside its defining `*Queries.cs` file (eliminating both false negatives on dedicated wrapper methods like
# `ShopAppProduct.FetchAsync` / `MagentoCart.SetBillingAsync` and false positives like generic `"item"`).
STR_AND_COMMENT = re.compile(
    r'"""[\s\S]*?"""|@"((?:[^"]|"")*)"|"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'|//[^\n]*|/\*[\s\S]*?\*/',
    re.S,
)
CONST_DECL = re.compile(r'(?:public|internal|private|protected)?\s*(?:const|static readonly)\s+string\s+(\w+)\s*=', re.M)
METHOD_DECL = re.compile(
    r'public\s+static\s+(?:async\s+)?(?:(?:Task|ValueTask)\s*<\s*\([^)]*\)\s*\??\s*>|[\w.<>?,\s\[\]]+)\s+(\w+)\s*\(',
    re.M,
)


def owner_class_name(path: str) -> str:
    cls = os.path.splitext(os.path.basename(path))[0]
    return cls[:-2] if cls.endswith('.g') else cls

code_only = {rel: STR_AND_COMMENT.sub(' ', text) for rel, text in all_src.items()}
non_comment_all = {
    rel: '\n'.join(l for l in text.splitlines() if not l.strip().startswith('//'))
    for rel, text in all_src.items()
}

# Map each image operation -> (defining_file, const_name)
op_consts = {}
for rel, text in all_src.items():
    for m in CONST_DECL.finditer(text):
        cname = m.group(1)
        end = text.find(';', m.end())
        if end < 0:
            continue
        span = text[m.end():end]
        for opm in PATTERN.finditer(span):
            op = opm.group(1)
            if op in image:
                op_consts.setdefault(op, []).append((rel, cname))

invoked_external = []
uninvoked_external = []
for op in covered:
    entries = op_consts.get(op, [])
    owners = def_files.get(op, set())
    is_invoked = False

    # Case A: defined directly inside a Flow / ThreeDs file (e.g. RetailFlows.cs, PayPalThreeDs.cs)
    if any(owner.endswith(('Flow.cs', 'Flows.cs', 'ThreeDs.cs')) for owner in owners):
        is_invoked = True

    # Case B: qualified `OwnerClass.CONST` referenced outside its defining file
    if not is_invoked:
        for owner, cname in entries:
            cls_name = owner_class_name(owner)
            cpat = re.compile(r'\b' + re.escape(cls_name) + r'\s*\.\s*' + re.escape(cname) + r'\b')
            if any(cpat.search(c) for r, c in code_only.items() if r != owner):
                is_invoked = True
                break

    # Case C: constant is used inside a dedicated static method of its owner class (or 1-hop via Envelope()),
    # and another production file calls `OwnerClass.MethodName`
    if not is_invoked:
        for owner, cname in entries:
            owner_txt = all_src[owner]
            cls_name = owner_class_name(owner)
            mdecls = list(METHOD_DECL.finditer(owner_txt))
            cpat = re.compile(r'\b' + re.escape(cname) + r'\b')
            method_bodies = []
            envelope_has_cname = False
            for idx, md in enumerate(mdecls):
                mname = md.group(1)
                mstart = md.start()
                mend = mdecls[idx + 1].start() if idx + 1 < len(mdecls) else len(owner_txt)
                mbody = owner_txt[mstart:mend]
                if mname == 'Envelope' and cpat.search(mbody):
                    envelope_has_cname = True
                method_bodies.append((mname, mbody))
            for mname, mbody in method_bodies:
                if mname in ('DocumentFor', 'Envelope'):
                    continue
                direct_hit = bool(cpat.search(mbody))
                one_hop_hit = (mname != 'SendAsync') and envelope_has_cname and bool(re.search(r'\bEnvelope\s*\(', mbody))
                if direct_hit or one_hop_hit:
                    call_pat = re.compile(r'\b' + re.escape(cls_name) + r'\s*\.\s*' + re.escape(mname) + r'\b')
                    if any(call_pat.search(c) for r, c in code_only.items() if r != owner):
                        is_invoked = True
                        break
            if is_invoked:
                break

    # Case D: dispatched via explicit `OwnerClass.<Method>(..., "op", ...)` in another file
    if not is_invoked:
        for owner in owners:
            cls_name = owner_class_name(owner)
            dispatch_pat = re.compile(
                r'\b' + re.escape(cls_name) + r'\s*\.\s*(?:Send|Document|Envelope|Query|Mutate|Execute|Run)\w*\s*\([^;]{0,240}"'
                + re.escape(op)
                + r'"',
                re.S,
            )
            if any(dispatch_pat.search(nc) for r, nc in non_comment_all.items() if r != owner):
                is_invoked = True
                break

    if is_invoked:
        invoked_external.append(op)
    else:
        uninvoked_external.append(op)

# Layer 3: scan Session.Vars side-door keys read in replica/src that have 0 production writers
var_read_pat = re.compile(r'Vars(?:\.(?:GetValueOrDefault|TryGetValue|ContainsKey)\(\s*"([^"]+)"|\[\s*"([^"]+)"\s*\](?!\s*=))')
var_write_pat = re.compile(r'Vars\s*\[\s*"([^"]+)"\s*\]\s*=')
writers_all = set()
readers_side_door = set()
for text in all_src.values():
    non_comment = '\n'.join(l for l in text.splitlines() if not l.strip().startswith('//'))
    for m in var_write_pat.finditer(non_comment):
        writers_all.add(m.group(1))
    for m in var_read_pat.finditer(non_comment):
        key = m.group(1) or m.group(2)
        if any(key.startswith(pref) for pref in SIDE_DOOR_PREFIXES):
            readers_side_door.add(key)
unwritten_side_doors = sorted(readers_side_door - writers_all)

print('image:   %d operations' % len(image))
print('replica: %d operations' % len(replica))
print('carried (text declared in src): %d of %d image operations (absent %d)' % (
    len(covered), len(image), len(missing)))
print('invoked from flow/gateway     : %d of %d (uninvoked in multi-op switches / dead classes: %d)' % (
    len(invoked_external), len(image), len(uninvoked_external)))
print('unwritten Session.Vars side-door keys (0 writers in replica/src): %d' % len(unwritten_side_doors))
print()

print('carried (%d): %s' % (len(covered), ', '.join(covered)))
print()
print('uninvoked outside defining file (%d): %s' % (len(uninvoked_external), ', '.join(uninvoked_external)))
print()
print('unwritten side-door keys (%d): %s' % (len(unwritten_side_doors), ', '.join(unwritten_side_doors)))
print()

print('absent (%d), longest first — the biggest payloads are the ones worth taking next:' % len(missing))
total = 0
for name in missing:
    entry = image[name]
    total += entry['length']
    print('   %-34s %6d chars   %s' % (name, entry['length'], entry['addr']))
print()
print('absent characters in total: %d' % total)
