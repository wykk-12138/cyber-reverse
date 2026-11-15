import io, re

text = io.open(r"D:\projects\cyber-reverse\analysis\pe_strings.txt",
               encoding="utf-8", errors="replace").read()

needles = ["history.length", "pushState", "replaceState", "maxTouchPoints", "touchEnabled",
           "cookieEnabled", "ontouchstart"]

for n in needles:
    print("==", n, "count", text.count(n))
    for m in list(re.finditer(re.escape(n), text))[:3]:
        i = m.start()
        print("   ", text[max(0, i - 100):i + 140].replace("\n", " | ")[:250])
    print()
