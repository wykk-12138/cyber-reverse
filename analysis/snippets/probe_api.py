# Probe which binary-search API this IDA build exposes, so the pointer scan uses a real name.
import ida_bytes
import idc

names = [n for n in dir(ida_bytes) if "find" in n.lower() or "bin" in n.lower()]
print("ida_bytes candidates: %s" % names)
print("idc candidates      : %s" % [n for n in dir(idc) if "find" in n.lower()][:20])
print("SEARCH_DOWN         : %s" % getattr(idc, "SEARCH_DOWN", None))
print("version             : %s" % idc.get_kernel_version() if hasattr(idc, "get_kernel_version") else "n/a")
