"""One-shot: fix the remaining mojibake line (R484, take 2).

The first pass only rewrote `（`x`）` shapes; this line has two backticked spans inside one parenthesis.
"""

import io

PATH = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
PREFIX = "2. 按字符码点匹配"
REPLACEMENT = "2. 按字符码点匹配 → 码点记错（用错了 Unicode 码点），脚本报 \"found 0\"；"

BAD = ("\u9225", "\ufffd")


def main():
    lines = io.open(PATH, encoding="utf-8").read().splitlines()
    for i, line in enumerate(lines):
        if line.startswith(PREFIX):
            print("before:", line[:110])
            lines[i] = REPLACEMENT
            print("after :", lines[i][:110])
    io.open(PATH, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    left = [i + 1 for i, line in enumerate(lines) if any(b in line for b in BAD)]
    print("remaining bad lines:", left)


if __name__ == "__main__":
    main()
