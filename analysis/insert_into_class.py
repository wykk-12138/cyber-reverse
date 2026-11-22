"""A reusable inserter: find the brace that actually closes a class, and put a method there.

R1369 paid for this once (rfind('}') is the file's last brace), and R1377 paid for it again. It is now a helper rather
than a thing I retype: `class_body_end(source, declaration)` walks from the declaration, skipping string literals and
comments, and returns the index of the closing brace.
"""


def class_body_end(source, declaration):
    """Index of the brace that closes the named class, skipping strings and comments."""
    start = source.find(declaration)
    if start < 0:
        raise ValueError('declaration not found: %s' % declaration)

    index = source.find('{', start)
    if index < 0:
        raise ValueError('declaration has no body: %s' % declaration)

    depth = 0
    while index < len(source):
        character = source[index]
        if character == '"':
            verbatim = index > 0 and source[index - 1] == '@'
            index += 1
            while index < len(source):
                if verbatim:
                    if source[index] == '"' and source[index + 1:index + 2] == '"':
                        index += 2
                        continue
                    if source[index] == '"':
                        break
                else:
                    if source[index] == '\\':
                        index += 2
                        continue
                    if source[index] == '"':
                        break
                index += 1
        elif character == '/' and source.startswith('//', index):
            newline = source.find('\n', index)
            if newline < 0:
                break
            index = newline
        elif character == '{':
            depth += 1
        elif character == '}':
            depth -= 1
            if depth == 0:
                return index
        index += 1

    raise ValueError('unbalanced class body: %s' % declaration)


def insert_before_class_end(source, declaration, block):
    """Insert a block just before the class's closing brace, keeping the brace at column zero."""
    close = class_body_end(source, declaration)
    return source[:close].rstrip('\n') + '\n' + block.rstrip('\n') + '\n' + source[close:]
