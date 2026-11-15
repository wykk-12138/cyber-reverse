import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\ChromiumBridge.cs"
lines = io.open(p, encoding="utf-8").read().split("\n")

# the block runs from the "// 3. plugins/mimeTypes" comment to the closing brace of its try
start = None
for i, line in enumerate(lines):
    if "// 3. plugins/mimeTypes" in line:
        start = i
        break

if start is None:
    raise SystemExit("plugins comment not found")

end = start
depth = 0
seen_try = False
while end < len(lines):
    if "try {" in lines[end]:
        seen_try = True
        depth += 1
    elif seen_try and lines[end].strip() == "} catch (e) {}":
        end += 1
        break
    end += 1

replacement = [
    "            // 3. plugins/mimeTypes: LEFT NATIVE (R169). Blink's lists are the spec's five PDF viewers and two mime",
    "            //    types, which is exactly what an iPhone reports and what the device collector reads. A patch here",
    "            //    used to answer three and none, so the earlier replica was further from the device than doing",
    "            //    nothing at all.",
    "",
]

lines[start:end + 1] = replacement
io.open(p, "w", encoding="utf-8", newline="").write("\n".join(lines))
print("the old plugin override is replaced by a note")
