import io, re

text = io.open(r"D:\projects\cyber-reverse\analysis\pe_strings.txt",
               encoding="utf-8", errors="replace").read()

for probe in ["__gCrWeb", "_injected_clipboard", "_injected_print", "_injected_choose_file",
              "_injected_setup_frame", "_injected_gcrweb", "_injected_autofill"]:
    hits = [m.start() for m in re.finditer(re.escape(probe), text)]
    print(f"{probe}: {len(hits)} hits")
    for i in hits[:3]:
        snippet = text[max(0, i - 220):i + 220].replace("\n", " | ")
        print("   ", snippet[:400])
    print()
