"""IDAPython: decompile the seven Cybersole pairs' original side to one file (R574).

Run inside IDA via `python analysis/ida.py py "exec(open('…/_run_dec7.py', encoding='utf-8').read())"`.

Why not seven `decompile` calls: each round trip re-encodes JSON, and the seven results are meant to be read
side by side against the replica's C# source. One file is the artefact the comparison needs.

The seven addresses come from `analysis/list_cybersole_pairs.py` — they are the only one-to-one hash matches whose
replica-side name starts with `Cybersole`, i.e. the only structural matches that land on the application layer
rather than on the shared runtime substrate (R573: 2,397 of 2,404 were corelib/Avalonia/Jint/CRT).
"""

import io

import ida_hexrays
import ida_funcs

OUT = r"D:\projects\cyber-reverse\analysis\_dec7_orig.txt"

# (original address, replica-side name it matched)
TARGETS = [
    (0x141998B80, "Cybersole.Services.NotificationService.SendWebhookAsync"),
    (0x14196AEA0, "Cybersole.Services.TaskEngine.<>c__DisplayClass22_0.<Ensure>b__0"),
    (0x141374A80, "Cybersole.Stores.Flows.ErrorCatalog.Entry.PrintMembers"),
    (0x140D31100, "Cybersole.Stores.Scripts.BrowserShim.Uuid"),
    (0x141375EF0, "Cybersole.Stores.Scripts.WindowOrder.Quote"),
    (0x140F7BB50, "Cybersole.Ui.ViewModels.MainViewModel.<>c__DisplayClass6_0.<.ctor>b__5"),
    (0x14042BB10, "Cybersole.Ui.Views.Utilities.UtilitiesView.<.ctor>b__10_0"),
]


def main():
    if not ida_hexrays.init_hexrays_plugin():
        print("hexrays unavailable")
        return 0

    ok = 0
    with io.open(OUT, "w", encoding="utf-8", newline="") as fh:
        for ea, replica_name in TARGETS:
            func = ida_funcs.get_func(ea)
            fh.write("=" * 100 + "\n")
            fh.write("ORIGINAL  0x%X  size=%d\n" % (ea, (func.end_ea - func.start_ea) if func else -1))
            fh.write("replica   %s\n" % replica_name)
            fh.write("=" * 100 + "\n")
            if func is None:
                fh.write("(no function at that address)\n\n")
                continue
            try:
                cf = ida_hexrays.decompile(func.start_ea)
            except Exception as exc:               # decompiler failure is data, not a crash
                fh.write("(decompile failed: %s)\n\n" % exc)
                continue
            if cf is None:
                fh.write("(decompile returned nothing)\n\n")
                continue
            fh.write(str(cf))
            fh.write("\n\n")
            ok += 1

    print("decompiled %d of %d -> %s" % (ok, len(TARGETS), OUT))
    return ok
