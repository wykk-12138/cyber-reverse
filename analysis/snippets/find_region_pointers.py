# Pointer scan for the IDA 9.x API: bin_search + parse_binpat_str.
# Looking for 8-byte values shaped 0x0143xxxxxx, i.e. little-endian ?? ?? ?? ?? 43 01 00 00,
# then keeping those inside the fake-data region 0x143600000..0x143800000.
import ida_bytes
import ida_segment
import idc

LO, HI = 0x143600000, 0x143800000

pat = ida_bytes.compiled_binpat_vec_t()
err = ida_bytes.parse_binpat_str(pat, 0, "?? ?? ?? ?? 43 01 00 00", 16)
if err:
    print("pattern parse error: %s" % err)
else:
    hits = []
    scanned = []
    for i in range(ida_segment.get_segm_qty()):
        seg = ida_segment.getnseg(i)
        if seg is None:
            continue
        name = ida_segment.get_segm_name(seg)
        if name not in (".rdata", ".data"):
            continue
        scanned.append("%s(%dKB)" % (name, (seg.end_ea - seg.start_ea) // 1024))
        ea = seg.start_ea
        while len(hits) < 100:
            res = ida_bytes.bin_search(ea, seg.end_ea, pat,
                                       ida_bytes.BIN_SEARCH_FORWARD | ida_bytes.BIN_SEARCH_NOSHOW)
            if res is None or res == idc.BADADDR:
                break
            hit_ea = res[0] if isinstance(res, tuple) else res
            if hit_ea == idc.BADADDR or hit_ea < ea:
                break
            val = idc.get_qword(hit_ea)
            if LO <= val < HI:
                hits.append((hit_ea, val))
            ea = hit_ea + 8
    print("scanned: %s" % ", ".join(scanned))
    print("pointers into region: %d" % len(hits))
    for at, val in hits[:20]:
        print("  at 0x%X -> 0x%X" % (at, val))
