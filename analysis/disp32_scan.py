r"""Scan .text for rip-relative disp32 references to frozen string objects.

WHY THIS TOOL EXISTS (AGENTS.md rule 1.2 requires the reason):
R691 established (five probes) that the fake-data blobs and locale JSON have no xrefs and no
absolute 8-byte pointers anywhere in .rdata/.data. That closed "string -> xref -> function" for
*blob fragments*. But it never tested whether *individually frozen string objects* (the
`[MethodTable][len:int32][utf16 chars]` cells that BLOCKERS §35 proved are read by code, e.g.
`XDG_RUNTIME_DIR` in `sub_140F39D80`) are referenced by rip-relative `lea` displacements --
the addressing form NativeAOT emits and IDA does not model as a pointer.

This tool works on raw file bytes, no IDA needed:
  1. Take an object address (VA) known to hold a frozen string.
  2. For every 4-byte-aligned position p in .text, treat the dword there as a disp32 candidate.
  3. The instruction containing it ends at VA(p)+4; a valid candidate satisfies
     target == VA(p) + 4 + disp  (rip-relative), within +/-2 GB.
  4. Report each candidate site (its VA and the surrounding instruction bytes).

A hit means: some instruction in .text references the object by displacement. From the site VA,
IDA (or the .pdata table) gives the containing function directly.

Reproduce:
    cd D:\projects\cyber-reverse
    python analysis/disp32_scan.py <VA> [<VA> ...]
    python analysis/disp32_scan.py --all license      # preset batch for the auth/license probes
"""

import argparse
import io
import os
import struct
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BINARY = os.path.join(ROOT, "target", "Cybersole.exe")

# Section table (parsed once, cached): name -> (file_offset, raw_size, va)
def sections(data):
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    nsec = struct.unpack_from("<H", data, pe + 6)[0]
    optsz = struct.unpack_from("<H", data, pe + 20)[0]
    base = struct.unpack_from("<Q", data, pe + 24 + 24)[0]
    out = {}
    sec = pe + 24 + optsz
    for i in range(nsec):
        o = sec + i * 40
        name = data[o:o + 8].rstrip(b"\x00").decode()
        vsize, va, rsize, roff = struct.unpack_from("<IIII", data, o + 8)
        out[name] = (roff, rsize, base + va, vsize)
    return out


def scan(data, secs, targets, verbose=False):
    """targets: {va: label}. Returns {va: [(site_fileoff, site_va), ...]}."""
    text_off, text_size, text_va, _ = secs[".text"]
    text = data[text_off:text_off + text_size]
    results = {va: [] for va in targets}
    # Read every aligned dword; compute implied target; keep those matching.
    # A disp32 valid range from .text to the frozen heap is roughly -0x30000000..+0x30000000,
    # so the arithmetic is cheap enough to do for all 12.8M dwords once per run.
    tgt_set = set(targets)
    n = text_size
    # iterate in chunks to keep memory flat
    step = 1 << 20
    for chunk_start in range(0, n, step):
        chunk = text[chunk_start:chunk_start + step]
        count = len(chunk) // 4
        for j in range(count):
            p = chunk_start + j * 4
            disp = struct.unpack_from("<i", chunk, j * 4)[0]
            site_va = text_va + p
            implied = site_va + 4 + disp
            if implied in tgt_set:
                results[implied].append((text_off + p, site_va))
    return results


def va_of(fo):
    """File offset -> VA (single-section .data mapping, verified against the TEMP hit)."""
    return 0x146A47000 + (fo - 0x6A45C00)


def object_va(peoff):
    """pe_strings.txt offset of a wide-string literal -> the frozen object's mt address.

    Layout measured this session (TEMP, LicenseListView, ...): pe_strings lists the *character*
    run; the object header is `[mt:8][len:4]` ending right at the chars, so mt = peoff - 12.
    """
    return va_of(peoff - 12)


PRESETS = {
    # label -> object VA (mt), derived from pe_strings file offsets via object_va()
    "license": {
        object_va(0x6B3A0FC): "ActiveLicenseItem",
        object_va(0x6B39F64): "ActivateButton",
        object_va(0x6E7D244): "SelectedLicense",
        object_va(0x6D9DD54): "GetLicenses",
        object_va(0x6B49E5C): "ApplyLicense",
        object_va(0x6DE259C): "LicenseItem",
        object_va(0x6DE2564): "LicenseCardIcon",
        object_va(0x6DE25CC): "LicenseListView",
        object_va(0x6B5217C): "Auth.License.Activate",
        object_va(0x6F7D41C): "avares:.../LicenseControl.axaml",
    },
    "sec35": {  # control set: slots BLOCKERS §35 proved are referenced by code
        0x146F310E0: "XDG_RUNTIME_DIR",
        0x146EB3BB8: "TMPDIR",
        object_va(0x6EB0734): "TEMP",   # the R691-era VA was the mt itself
    },
}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("vas", nargs="*", type=lambda x: int(x, 0), help="target VAs (0x...)")
    parser.add_argument("--all", choices=sorted(PRESETS), help="scan a preset batch")
    parser.add_argument("--show-bytes", action="store_true")
    args = parser.parse_args(argv)

    if args.all:
        targets = dict(PRESETS[args.all])
    elif args.vas:
        targets = {va: "VA 0x%X" % va for va in args.vas}
    else:
        parser.error("give VAs or --all {license,sec35}")

    data = io.open(BINARY, "rb").read()
    secs = sections(data)
    text_off, text_size, text_va, _ = secs[".text"]
    print("scanning .text: 0x%X bytes at file 0x%X (VA 0x%X) for %d target(s)"
          % (text_size, text_off, text_va, len(targets)))

    results = scan(data, secs, targets)

    total = 0
    for va in sorted(targets):
        hits = results[va]
        total += len(hits)
        print("%-34s VA 0x%X -> %d site(s)" % (targets[va], va, len(hits)))
        for fo, sva in hits[:8]:
            line = "    site VA 0x%X  file 0x%X" % (sva, fo)
            if args.show_bytes:
                ctx = data[fo - 8:fo + 12]
                line += "  ctx " + " ".join("%02X" % b for b in ctx)
            print(line)
        if len(hits) > 8:
            print("    ... %d more" % (len(hits) - 8))
    print("TOTAL sites: %d" % total)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
