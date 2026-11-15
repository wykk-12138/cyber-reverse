import io

text = io.open(r"D:\projects\cyber-reverse\analysis\pe_strings.txt",
               encoding="utf-8", errors="replace").read()

for needle in ["const SCREEN = {", "const VV = {", "orientation"]:
    i = text.find(needle)
    print("==", needle, "at", i)
    if i >= 0:
        print(text[i:i + 900])
    print()
