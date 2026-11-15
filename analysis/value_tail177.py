import io

text = io.open(r"D:\projects\cyber-reverse\analysis\pe_strings.txt",
               encoding="utf-8", errors="replace").read()

i = text.find("const value = (target, name, v, enumerable) => {")
print("offset", i)
print(text[i + 2600:i + 5600])
