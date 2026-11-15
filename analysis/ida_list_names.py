# list IDA names that mention TaskView / Toggle, then quit
import idautils, idc, idaapi
out = r"D:\projects\cyber-reverse\analysis\ida_names_taskview.txt"
hits = []
for ea, name in idautils.Names():
    if 'TaskView' in name or 'Toggle' in name:
        hits.append("%08X\t%s" % (ea, name))
open(out, 'w', encoding='utf-8').write("\n".join(hits))
print("names matched:", len(hits))
idc.qexit(0)
