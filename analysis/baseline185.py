import io, re

text = io.open(r"D:\projects\cyber-reverse\analysis\pe_strings.txt",
               encoding="utf-8", errors="replace").read()

# the assignment on the last line, and the topList function again with its full body
for anchor in ["WINDOW_BASELINE = new Set", "WINDOW_BASELINE =", "const topList"]:
    i = text.find(anchor)
    print("=" * 24, anchor, "at", i)
    if i > 0:
        print(text[max(0, i - 900):i + 900])
