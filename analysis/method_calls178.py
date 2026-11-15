import io, re

text = io.open(r"D:\projects\cyber-reverse\analysis\pe_strings.txt",
               encoding="utf-8", errors="replace").read()

# every call site of method(...) / canvas / audio patches in the injected block
for pattern in [r"method\((?:[A-Za-z_.\[\]' ]+), '[A-Za-z]+'", r"C\.(?:fillText|getImageData|toDataURL|toBlob|measureText)"]:
    hits = list(re.finditer(pattern, text))
    print(pattern, "->", len(hits))
    for m in hits[:12]:
        i = m.start()
        line_start = text.rfind("\n", 0, i)
        print("   ", text[i:i + 120].replace("\n", " "))
