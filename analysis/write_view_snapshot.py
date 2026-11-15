import io, re

res = io.open(r"C:\Users\wykk\AppData\Local\Cybersole\analysis\avalonia_resources.txt",
              encoding="utf-8", errors="replace").read()

pairs = re.findall(r"<a:Key>(Cybersole\.Ui\.[^<]+)</a:Key><a:Value>([^<]+)</a:Value>", res)
rows = sorted((k.rsplit(".", 1)[-1], v) for k, v in pairs)
print("classes:", len(rows))

header = """# The original's view classes, exactly as the binary's Avalonia index lists them
#
# Source: ClassToResourcePathIndex inside the Avalonia resource manifest of Cybersole.exe 5.18.30
#         (analysis/avalonia_resources.txt). 87 entries.
#
# Format: <class>  <resource path>
#
# This file exists so OriginalViewClassParityTests can compare the replica against the original
# without needing the binary present. It is a snapshot, not a wish list: every line was read off
# the binary, so a line may only be removed if the binary changes.

"""

body = "".join("%-40s %s\n" % (name, path) for name, path in rows)
io.open(r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\original_view_classes.txt",
        "w", encoding="utf-8", newline="").write(header + body)
print("written")
