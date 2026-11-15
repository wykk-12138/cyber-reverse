from PIL import Image
p = r"D:\projects\cyber-reverse\analysis\proxies_now.png"
im = Image.open(p).convert("RGB"); px = im.load(); W, H = im.size
print("screen", W, H)
# scan a horizontal line inside the rail area (y=400) for the vertical border between rail and table
y = 400
prev = None
edges = []
for x in range(0, W):
    r, g, b = px[x, y]
    lum = (r + g + b) // 3
    if prev is not None and abs(lum - prev) > 6:
        edges.append((x, prev, lum))
    prev = lum
print("edges on y=%d:" % y, edges[:14])
