import io

text = io.open(r"D:\projects\cyber-reverse\analysis\pe_strings.txt",
               encoding="utf-8", errors="replace").read()

for anchor in [
    "method(Function.prototype, 'bind'",
    "method(JSON, 'stringify'",
    "method(Reflect, 'ownKeys'",
]:
    i = text.find(anchor)
    print("=" * 30, anchor)
    print(text[max(0, i - 1400):i + 1200])
