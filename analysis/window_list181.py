import io, re

text = io.open(r"D:\projects\cyber-reverse\analysis\pe_strings.txt",
               encoding="utf-8", errors="replace").read()

# the window name array ends with "__gCrWeb"
end = text.find('"__gCrWeb"];')
start = text.rfind("[", 0, end - 200000) if end > 0 else -1

# walk back to the opening bracket of the array that contains __gCrWeb
i = text.rfind('const WINDOW_ALL', 0, end)
if i < 0:
    i = text.rfind('= [', 0, end)
print("window list anchor at", i, "end", end)

segment = text[i:end + len('"__gCrWeb"];')]
names = re.findall(r'"([^"]+)"', segment)
print("names:", len(names))
print("first 20:", names[:20])
print("last 10:", names[-10:])

# does it include the two frame-only names?
for probe in ["_injected_scroll_helper", "_injected_navigation", "webkit", "Raven"]:
    print(probe, "->", probe in names)
