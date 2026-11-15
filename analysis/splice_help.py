import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Settings\ProviderViews.cs"
lines = io.open(p, encoding="utf-8").read().split("\n")

# HelpView runs from its doc comment to its closing brace on line 1454 (1-based).
start_marker = "/// <summary>Need help (Cybersole.Ui.Views.Settings.HelpView).</summary>"
start = None
for i, line in enumerate(lines):
    if line.strip() == start_marker:
        start = i
        break
if start is None:
    raise SystemExit("HelpView doc comment not found")

# closing brace of the class: first line that is exactly "}" after the class declaration
decl = None
for i in range(start, min(start + 20, len(lines))):
    if "class HelpView" in lines[i]:
        decl = i
        break
if decl is None:
    raise SystemExit("class declaration not found")

end = None
for i in range(decl, len(lines)):
    if lines[i] == "}":
        end = i
        break
if end is None:
    raise SystemExit("class end not found")

block = io.open(r"C:\Users\wykk\AppData\Local\Cybersole\analysis\r81_help_view.cs.txt",
                encoding="utf-8").read().split("\n")

# strip a trailing empty string from the split so the join does not add a blank line
if block and block[-1] == "":
    block = block[:-1]

new_lines = lines[:start] + block + lines[end + 1:]
io.open(p, "w", encoding="utf-8", newline="").write("\n".join(new_lines))
print("HelpView replaced: lines %d..%d -> %d lines" % (start + 1, end + 1, len(block)))
