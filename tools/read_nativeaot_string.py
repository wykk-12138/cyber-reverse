# WHY THIS EXISTS: same as _tmp_fields.py -- &off_XXX operands are String object headers in NativeAOT,
# chars start at +12. This run resolves the only two operands that differ between the /botid and /payload
# request builders. ASCII only; writes a file.
def main():
    import ida_bytes

    out_path = r"D:\projects\cyber-reverse\.tmp-fields2.txt"
    lines = []
    slots = [
        ("botid status", 0x146DA1588),
        ("payload status", 0x146DA1778),
        ("white", 0x147184330),
        ("statusinfo", 0x146E9B830),
        ("typeval", 0x1470AE4B8),
        ("method", 0x146E34DB8),
        ("enc", 0x14718F7C8),
        ("hdr-upstream-url", 0x146F2E098),
        ("hdr-type", 0x146F2DFC0),
        ("hdr-client-ver", 0x146F2D8B8),
        ("hdr-upstream-method", 0x146F2E060),
        ("hdr-upstream-headers", 0x146F2E020),
        ("hdr-user-id", 0x146F2E0D0),
        ("content-encoding", 0x146FD6628),
    ]

    def s16(ea):
        length = ida_bytes.get_dword(ea + 8)
        if length is None or length < 0 or length > 256:
            return "<len=%s>" % length
        raw = ida_bytes.get_bytes(ea + 12, length * 2)
        return raw.decode("utf-16-le", "replace") if raw else "<no bytes>"

    for label, ea in slots:
        lines.append("%-22s %s  ->  %r" % (label, hex(ea), s16(ea)))

    f = open(out_path, "w", encoding="utf-8")
    f.write("\n".join(lines))
    f.close()
    return "wrote %s lines=%d" % (out_path, len(lines))


main()
