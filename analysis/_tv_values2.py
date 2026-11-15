import io, re
raw = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read()
want = ['Tasks.LinkChange.InvalidTitle','Tasks.LinkChange.InvalidMessage','Tasks.Quicktask.InvalidTitle','Tasks.Quicktask.InvalidMessage','Monitor.LinkChange','Monitor.LaunchQuicktask','KeyBinds.Tasks.LinkChange','KeyBinds.Tasks.Quicktask','Settings.General.QuicktaskSettings']
for k in want:
    # values live in the SAME string, right after the key + '": "'
    for m in re.finditer(re.escape('"') + re.escape(k) + r'":\s*"([^"]*)"', raw):
        print('%-34s => %s' % (k, m.group(1)))
        break
    else:
        print('%-34s => (value not on one line)' % k)
