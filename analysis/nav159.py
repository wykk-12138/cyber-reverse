import io

text = io.open(r"D:\projects\cyber-reverse\analysis\pe_strings.txt",
               encoding="utf-8", errors="replace").read()

i = text.find("const NAV = {")
print("offset", i)
print(text[i:i + 2600])
