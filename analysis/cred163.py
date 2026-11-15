import io, re

text = io.open(r"D:\projects\cyber-reverse\analysis\pe_strings.txt",
               encoding="utf-8", errors="replace").read()

i = text.find("const CRED_SHIM")
print("offset", i)
print(text[i:i + 1400])

print()
print("=== credentials mentions")
for m in list(re.finditer(r"credentials", text))[:8]:
    j = m.start()
    print("   ", text[max(0, j - 90):j + 110].replace("\n", " | ")[:200])
