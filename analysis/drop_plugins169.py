import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\MobileSurface.cs"
t = io.open(p, encoding="utf-8").read()

start = t.find("        // 1. five plugins, and a length that matches the list rather than a fixed number")
end = t.find("        // 2. the connection quartet")

if start < 0 or end < start:
    raise SystemExit("plugins block not found")

replacement = '''        // 1. plugins and mimeTypes are left NATIVE (R169). The image's own note is decisive: Blink's lists are the
        //    spec's five PDF viewers — all `internal-pdf-viewer` — and two PDF mime types, which is exactly what an
        //    iPhone reports, and the device collector reads lengths 5 / 2. An override used to empty both, on the
        //    mistaken belief that WebKit's lists are empty, so every bot payload carried `plugins: []`.
        //
        //    So the only correct patch here is none. Kept as a comment so the next reader does not add one back.

'''

t = t[:start] + replacement + t[end:]
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("the plugin override is gone; the native lists stand")
