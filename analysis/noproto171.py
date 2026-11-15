import io, re

text = io.open(r"D:\projects\cyber-reverse\analysis\pe_strings.txt",
               encoding="utf-8", errors="replace").read()

for m in list(re.finditer(r"noProtoMethod", text))[:6]:
    i = m.start()
    print("---")
    print(text[max(0, i - 260):i + 320])
