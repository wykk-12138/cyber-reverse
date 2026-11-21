"""Does CasioFlow already override GetCartAsync? Ask per class, not per file.

The previous attempt refused because RetailFlows.cs contains GetCartAsync somewhere — the file holds many flow
classes, so a file-wide check answers the wrong question. This walks each class body by brace matching and
reports which class owns each override, which is the check R1320-R1322 needed and did not have.

Usage: python analysis/which_class_has.py GetCartAsync
"""
import io
import sys

PATH = 'replica/src/Cybersole.Stores/Flows/RetailFlows.cs'
needle = sys.argv[1] if len(sys.argv) > 1 else 'GetCartAsync'

text = io.open(PATH, encoding='utf-8').read()

classes = []
for index, char in enumerate(text):
    if text.startswith('public sealed class ', index) or text.startswith('public class ', index):
        name_start = index + len('public sealed class ') if text.startswith('public sealed class ', index) \
            else index + len('public class ')
        name = text[name_start:].split()[0]
        brace = text.index('{', name_start)
        depth = 0
        for position in range(brace, len(text)):
            if text[position] == '{':
                depth += 1
            elif text[position] == '}':
                depth -= 1
                if depth == 0:
                    classes.append((name, brace, position))
                    break

print('classes found: %d' % len(classes))
for name, start, end in classes:
    body = text[start:end]
    if needle in body:
        line = text[:start].count('\n') + 1
        count = body.count(needle)
        print('  %-24s line %5d   %s x%d' % (name, line, needle, count))
