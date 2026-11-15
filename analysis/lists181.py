import io

text = io.open(r"D:\projects\cyber-reverse\analysis\pe_strings.txt",
               encoding="utf-8", errors="replace").read()

# the two recorded lists the reorder needs: WINDOW_BASELINE and CSS_DECL
for name in ["WINDOW_BASELINE", "CSS_DECL"]:
    i = text.find("const " + name)
    if i < 0:
        i = text.find(name + " = ")
    print("=" * 20, name, "at", i)
    if i > 0:
        print(text[max(0, i - 700):i + 500])
