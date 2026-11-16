r"""disp32 scan at EVERY byte offset (numpy), closing the alignment blind spot.

WHY THIS TOOL EXISTS (AGENTS.md rule 1.2):
disp32_scan.py only tests 4-byte-aligned positions. Measured this session: `Auth.License.Activate`
(obj VA 0x146B53570) is referenced by sub_140765730 (decompiler emits `off_146B53570` at line
2303) yet the aligned scan reports 0 sites -- the lea's disp32 field sits at an unaligned
offset. So "0 aligned hits" cannot close a question. This variant slides over every byte of
.text (numpy-vectorised) so a miss here is a real miss.

Usage:
    python analysis/disp32_scan_any.py <VA> [<VA> ...]
    python analysis/disp32_scan_any.py --all license_csv
"""
import argparse
import io
import os
import struct
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BINARY = os.path.join(ROOT, "target", "Cybersole.exe")

TEXT_OFF, TEXT_SIZE, TEXT_VA = 0x400, 0x314CE00, 0x140001000


def object_va(peoff):
    """pe_strings file offset -> frozen wide-string object VA (mt at chars-12, measured)."""
    return 0x146A47000 + (peoff - 12 - 0x6A45C00)


PRESETS = {
    "license_csv": {
        object_va(0x06E4BD6C): "ProfileCsv.Error.UnknownCountry",
        object_va(0x06E4BDC4): "ProfileCsv.Error.UnknownState",
        # controls from the same view, for triangulation
        object_va(0x06E4BB3C): "ProfileCsv.Apply",
        object_va(0x06E4BC0C): "ProfileCsv.DeleteRows",
    },
    "license_ctl": {  # re-run of the license batch with the blind spot closed
        object_va(0x06B49E5C): "ApplyLicense",
        object_va(0x06D9DD54): "GetLicenses",
        object_va(0x06E7D244): "SelectedLicense",
        object_va(0x06B5217C): "Auth.License.Activate",
    },
}


def scan(data, targets):
    b = np.frombuffer(data[TEXT_OFF:TEXT_OFF + TEXT_SIZE], dtype=np.uint8)
    n = len(b) - 4
    disp = (b[:n].astype(np.int64)
            | (b[1:n + 1].astype(np.int64) << 8)
            | (b[2:n + 2].astype(np.int64) << 16)
            | (b[3:n + 3].astype(np.int64) << 24))
    # sign-extend from 32 bits
    disp = np.where(disp >= 0x80000000, disp - 0x100000000, disp)
    site_va = np.arange(n, dtype=np.int64) + TEXT_VA + 4
    implied = site_va + disp
    out = {va: [] for va in targets}
    tgt = np.array(sorted(targets), dtype=np.int64)
    idx = np.searchsorted(tgt, implied)
    idx_clipped = np.clip(idx, 0, len(tgt) - 1)
    match = tgt[idx_clipped] == implied
    positions = np.nonzero(match)[0]
    for p in positions:
        out[int(tgt[idx_clipped[p]])].append(TEXT_OFF + int(p))
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("vas", nargs="*", type=lambda x: int(x, 0))
    parser.add_argument("--all", choices=sorted(PRESETS))
    parser.add_argument("--show-bytes", action="store_true")
    args = parser.parse_args(argv)

    if args.all:
        targets = dict(PRESETS[args.all])
    elif args.vas:
        targets = {va: "VA 0x%X" % va for va in args.vas}
    else:
        parser.error("give VAs or --all")

    data = io.open(BINARY, "rb").read()
    print("unaligned scan: .text 0x%X bytes, %d target(s)" % (TEXT_SIZE, len(targets)))
    results = scan(data, targets)

    total = 0
    for va in sorted(targets):
        hits = results[va]
        total += len(hits)
        print("%-34s VA 0x%X -> %d site(s)" % (targets[va], va, len(hits)))
        for fo in hits[:10]:
            line = "    file 0x%X  VA 0x%X" % (fo, fo - TEXT_OFF + TEXT_VA)
            if args.show_bytes:
                ctx = data[fo - 8:fo + 12]
                line += "  ctx " + " ".join("%02X" % x for x in ctx)
            print(line)
        if len(hits) > 10:
            print("    ... %d more" % (len(hits) - 10))
    print("TOTAL sites: %d" % total)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
