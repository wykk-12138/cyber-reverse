import io

text = io.open(r"D:\projects\cyber-reverse\analysis\pe_strings.txt",
               encoding="utf-8", errors="replace").read()

i = text.find("method(Reflect, 'ownKeys'")
print("offset", i)
print(text[max(0, i - 5200):i + 900])
