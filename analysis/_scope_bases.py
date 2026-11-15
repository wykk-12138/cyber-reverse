import io, re
p = r"D:\projects\cyber-reverse\replica\tools\bind_scope.py"
t = io.open(p, encoding='utf-8').read()

t = t.replace('''DECL = re.compile(r"\\b(?:class|interface|record|struct)\\s+(\\w+)[^;{]*\\{")''',
'''DECL = re.compile(r"\\b(?:class|interface|record|struct)\\s+(\\w+)\\s*(?::\\s*([^;{]+?))?\\s*(?:where[^;{]*)?\\{")''')

t = t.replace('''                for index in range(start, len(text)):
                    if text[index] == "{":
                        depth += 1
                    elif text[index] == "}":
                        depth -= 1
                        if depth == 0:
                            found.setdefault(match.group(1), []).append(text[start:index + 1])
                            break
    return found''',
'''                for index in range(start, len(text)):
                    if text[index] == "{":
                        depth += 1
                    elif text[index] == "}":
                        depth -= 1
                        if depth == 0:
                            found.setdefault(match.group(1), []).append(text[start:index + 1])
                            bases.setdefault(match.group(1), []).extend(
                                b.split(".")[-1].split("<")[0].strip()
                                for b in (match.group(2) or "").split(",")
                                if b.strip())
                            break
    return found, bases''')

t = t.replace('''    found = {}
    for dirpath''', '''    found = {}
    bases = {}
    for dirpath''')

t = t.replace('''    binds = json.load(io.open(BINDS, encoding="utf-8"))
    bodies = bodies_by_name()''',
'''    binds = json.load(io.open(BINDS, encoding="utf-8"))
    bodies, bases = bodies_by_name()

    def with_bases(name, seen=None):
        """The type's body plus every ancestor's — members inherited from a base are not missing."""
        seen = seen or set()
        if name in seen:
            return ""
        seen.add(name)
        text = "\\n".join(bodies.get(name, []))
        for base in bases.get(name, []):
            text += "\\n" + with_bases(base, seen)
        return text''')

t = t.replace('''        merged = "\\n".join(parts)''', '''        merged = with_bases(short)''')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('base-class resolution added')
