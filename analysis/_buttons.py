from PIL import Image
p = r"C:\Users\wykk\.dsh\attachments\v1\objects\1d\1d2648ed1ffb14ff8f33dfa4d94c5079c4664c46de7e66288481b9a334dba1aa"
im = Image.open(p).convert("RGB"); px = im.load(); W, H = im.size
print("tasks page", W, H)
# Bottom button row: find rows whose pixels contain saturated colour (green/red/blue buttons)
def is_colour(c, minv=70, maxv=250):
    r, g, b = c
    mx, mn = max(r, g, b), min(r, g, b)
    return mx > 90 and (mx - mn) > 40
rows = []
for y in range(H - 150, H):
    n = sum(1 for x in range(0, W) if is_colour(px[x, y]))
    if n > 60: rows.append((y, n))
print("colour rows:", rows[:6], "...", rows[-6:] if rows else None)
if rows:
    y0, y1 = rows[0][0], rows[-1][0]
    print("button band y:", y0, "..", y1, "height", y1 - y0 + 1)
    # column extents on the middle line of the band
    ym = (y0 + y1) // 2
    runs, cur = [], None
    for x in range(W):
        if is_colour(px[x, ym]):
            cur = [x, x] if cur is None else [cur[0], x]
        else:
            if cur and cur[1] - cur[0] > 20: runs.append((cur[0], cur[1], cur[1] - cur[0] + 1))
            cur = None
    if cur and cur[1] - cur[0] > 20: runs.append((cur[0], cur[1], cur[1] - cur[0] + 1))
    print("coloured buttons (x0, x1, width):", runs)
