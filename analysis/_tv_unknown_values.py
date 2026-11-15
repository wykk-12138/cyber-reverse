import io, re
lines = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
rows = [m.group(2).strip() for m in (re.match(r'^\s*(0x[0-9a-f]+)\s+(.*)$', l) for l in lines) if m]
want = ('Tasks.LinkChange.InvalidTitle','Tasks.LinkChange.InvalidMessage','Tasks.Quicktask.InvalidTitle','Tasks.Quicktask.InvalidMessage','Monitor.LinkChange','Monitor.LaunchQuicktask','KeyBinds.Tasks.LinkChange','KeyBinds.Tasks.Quicktask','Settings.General.QuicktaskSettings')
for k in want:
    vals = sorted({r for r in rows if r.startswith('"' + k + '":')})
    print(k, '=>', vals[0][:160] if vals else '(no value)')
