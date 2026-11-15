import io, re

text = io.open(r"D:\projects\cyber-reverse\analysis\pe_strings.txt",
               encoding="utf-8", errors="replace").read()

needles = ["ScreenOrientation", "portrait-primary", "portrait-secondary",
           "landscape-primary", "lockOrientation", "orientation.lock"]

for n in needles:
    print("==", n, "count", text.count(n))
    for m in list(re.finditer(re.escape(n), text))[:4]:
        i = m.start()
        seg = text[max(0, i - 120):i + 120].replace("\n", " | ")
        print("   ", seg[:240])
    print()
