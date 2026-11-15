import io

text = io.open(r"D:\projects\cyber-reverse\analysis\pe_strings.txt",
               encoding="utf-8", errors="replace").read()

i = text.find("const toStringPatched = noProtoMethod")
print("offset", i)
print(text[max(0, i - 1800):i + 1600])
