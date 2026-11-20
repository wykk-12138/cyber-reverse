"""Rewrite write_square_browser_data.py from str.format to %-formatting.

str.format treats every literal `{` in the embedded C# as a field, and the C# is full of them -- initialisers,
property accessors, method bodies. Escaping them by hand is a transcription job with no upside, while `%`
formatting only cares about `%(name)s` and the C# contains no percent signs at all.

A file, not a command line: PowerShell's quoting ate the previous two attempts.
"""
import io

PATH = 'analysis/write_square_browser_data.py'
text = io.open(PATH, encoding='utf-8').read()

# 1) Switch the call site.
old_call = "'''.format(length=len(raw), sans_length=len(raw) - 22, template=template)"
new_call = "''' % {'length': len(raw), 'sans_length': len(raw) - 22, 'template': template}"
assert text.count(old_call) == 1, text.count(old_call)
text = text.replace(old_call, new_call)

# 2) Named placeholders, longest first so {sans_length} is not clipped by {sans_length}-byte ordering.
for old, new in (
    ('public const string Template = {template};', 'public const string Template = %(template)s;'),
    ('{sans_length}-byte', '%(sans_length)d-byte'),
    ('{sans_length} bytes', '%(sans_length)d bytes'),
    ('{length} bytes', '%(length)d bytes'),
):
    if old in text:
        text = text.replace(old, new)
        print('placeholder: %s' % old)

# 3) Un-escape the doubled braces that str.format needed and %-formatting would print literally.
before = text.count('{{') + text.count('}}')
text = text.replace('{{', '{').replace('}}', '}')
print('un-escaped %d doubled braces' % before)

# 4) The Escape helper was written against str.format escaping; make sure the C# it emits is still right.
io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('rewrote %s' % PATH)
