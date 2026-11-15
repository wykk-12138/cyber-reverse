from PIL import Image
def rail(path, y):
    im = Image.open(path).convert("RGB"); px = im.load(); W, H = im.size
    def lum(c): return (c[0]*299 + c[1]*587 + c[2]*114)//1000
    vals = [lum(px[x, y]) for x in range(W)]
    base = sorted(vals)[len(vals)//2]
    runs, cur = [], None
    for x, v in enumerate(vals):
        if v > base + 3:
            cur = [x, x] if cur is None else [cur[0], x]
        else:
            if cur and cur[1]-cur[0] > 40: runs.append(tuple(cur))
            cur = None
    if cur and cur[1]-cur[0] > 40: runs.append(tuple(cur))
    return W, H, runs[:6]

a = r"C:\Users\wykk\.dsh\attachments\v1\objects\f9\f92901e4539cb15736c4d316424dcd3fb1ead7c7b51b0a039688cace53288f88"
b = r"C:\Users\wykk\.dsh\attachments\v1\objects\0c\0cc4fb6be46306ec07428a0fc47e93153ac84135c99546714d88d13d22b28dcc"
print("1375 wide:", rail(a, 235))
print("1566 wide:", rail(b, 235))
