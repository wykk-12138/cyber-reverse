import io, re, collections

p = r"D:\projects\cyber-reverse\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

print("=== *.cybersole.io hosts")
for host in sorted(set(re.findall(r"[a-z0-9\-\.]+\.cybersole\.io", text))):
    print("   ", host)

print()
print("=== literals containing 'solver' (case-insensitive, distinct)")
seen = []
for line in text.split("\n"):
    body = line.split("  ", 1)[-1]
    if "solver" in body.lower() and body not in seen:
        seen.append(body)
        print("   ", body[:140])
        if len(seen) >= 14:
            break

print()
print("=== candidate kasada endpoints (host/path with kasada|kpsdk|/tl)")
for m in sorted(set(re.findall(r"https?://[A-Za-z0-9\-\.]+/[A-Za-z0-9_\-/]*(?:kasada|kpsdk|/tl)[A-Za-z0-9_\-/?=&.]*", text, re.I))):
    print("   ", m[:120])
