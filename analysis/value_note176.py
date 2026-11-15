import io

text = io.open(r"D:\projects\cyber-reverse\analysis\pe_strings.txt",
               encoding="utf-8", errors="replace").read()

i = text.find("// A value installed as an accessor, with the descriptor shape of a real one.")
print("offset", i)
print(text[i:i + 3200])
