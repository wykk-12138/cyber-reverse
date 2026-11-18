"""R1159: is the 3DS/hosted family stored as a pointer table?

R1158 showed init-challenge is referenced by neither xref nor a .text byte scan, and concluded a pointer
table in the data segments is the likely answer. If the family sits in one managed array, the array's
element order *is* the hosted step order, which is exactly the thing the replica has been guessing at.

Method: take the object address of every PayPal literal this project already knows, find where each
appears as a little-endian 8-byte pointer anywhere in the image, then report clusters -- three or more
pointers within 64 bytes of each other are a table, and each cluster is printed with the strings it
points at so the order reads out directly.
"""
import ida_bytes
import ida_ida
import idautils
import idc

# chars_va values recorded in earlier rounds; the object is chars - 12.
LIMIT = 8
KNOWN = {
    0x147097E78: "graphql/",
    0x147097F60: "graphql?GetThreeDsJwtQuery",
    0x147098058: "graphql?ResolveThreeDsContingency",
    0x1470980E0: "graphql?ThreeDsAuthenticateMutation",
    0x147098170: "graphql?ThreeDsLookUpMutation",
    0x147098540: "threeds/v1/init-challenge",
    0x1470985E8: "threeds/v1/init-method",
    0x147098688: "threeds/v1/notify-challenge-cmpl/",
    0x147098740: "threeds/v1/notify-method-cmpl",
    0x1470983D8: "heliosnext/threeDS?action=verify",
    0x1470982F0: "heliosnext/api/serverData",
    0x147098368: "heliosnext/api/session",
    0x147098258: "heliosnext/api/processThreedsConfirmation",
    0x147097D08: "checkoutweb/processThreedsConfirmation",
    0x14709910C: "v2/checkout/orders",
    0x147099174: "v2/checkout/orders/",
    0x147163128: "challenge fragment",
}


def frozen(va):
    raw = ida_bytes.get_bytes(va, 12)
    if not raw or len(raw) < 12:
        return None
    ln = int.from_bytes(raw[8:12], "little")
    if not (0 < ln < 20000):
        return None
    body = ida_bytes.get_bytes(va + 12, ln * 2)
    if not body or len(body) < ln * 2:
        return None
    try:
        return body.decode("utf-16-le")
    except UnicodeDecodeError:
        return None


lo, hi = ida_ida.inf_get_min_ea(), ida_ida.inf_get_max_ea()
print("image %#x..%#x" % (lo, hi))

hits = {}
for chars in KNOWN:
    obj = chars - 12
    needle = obj.to_bytes(8, "little")
    found = []
    # ida_bytes.bin_search refuses bytes+None on this build (R1143 hit the same wall three times), so
    # the scan reads segment bytes in chunks and uses plain bytes.find instead of fighting the overload.
    for start in idautils.Segments():
        seg_end = idc.get_segm_end(start)
        if idc.get_segm_attr(start, idc.SEGATTR_TYPE) == 2:   # SEG_CODE: a string object cannot live here
            continue
        pos = start
        while pos < seg_end and len(found) <= 40:
            size = min(8 * 1024 * 1024, seg_end - pos)
            chunk = ida_bytes.get_bytes(pos, size)
            if not chunk:
                pos += size
                continue
            at = chunk.find(needle)
            while at >= 0 and len(found) <= 40:
                found.append(pos + at)
                at = chunk.find(needle, at + 1)
            pos += size - 7
    hits[obj] = found
    print("%-34s obj %#x  stored-at %d" % (KNOWN[chars], obj, len(found)))

# cluster: pointers that sit within 64 bytes of one another
points = sorted((ea, obj) for obj, eal in hits.items() for ea in eal)
clusters, current = [], []
for ea, obj in points:
    if current and ea - current[-1][0] > 64:
        if len(current) >= 3:
            clusters.append(current)
        current = []
    current.append((ea, obj))
if len(current) >= 3:
    clusters.append(current)

print()
print("clusters (>=3 pointers within 64 bytes):", len(clusters))
for c in clusters[:6]:
    print("  table near %#x  (%d pointers)" % (c[0][0], len(c)))
    for ea, obj in c[:12]:
        s = frozen(obj)
        print("     +%3d %#x -> %r" % (ea - c[0][0], obj, (s or "?")[:60]))
