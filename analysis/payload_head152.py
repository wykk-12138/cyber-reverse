import io

text = io.open(r"D:\projects\cyber-reverse\analysis\pe_strings.txt",
               encoding="utf-8", errors="replace").read()

i = text.find("window.screen.orientation.type")
start = max(0, i - 3600)

# find the beginning of the JSON-looking payload
head = text.find('{"', start)
if head < 0 or head > i:
    head = start

print(text[head:i - 1200])
