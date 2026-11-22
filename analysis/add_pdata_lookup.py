"""Add a function-range lookup to the direct reader, using the image's own .pdata table.

`.pdata` holds RUNTIME_FUNCTION records — begin RVA, end RVA, unwind RVA — sorted by begin, so a site address can be
resolved to its function without IDA. That answers "which functions reference this string", which is the half of the
job that does not need a disassembler.
"""
import io

PATH = 'analysis/pe_read_direct.py'
text = io.open(PATH, encoding='utf-8').read()

if 'def function_start' in text:
    raise SystemExit('already present')

helper = '''
    def pdata_functions(self):
        """(begin_va, end_va) pairs from .pdata, in file order."""
        for section in self.sections:
            if not section['name'].startswith('.pdata'):
                continue
            count = min(section['vsize'], section['raw_size']) // 12
            pairs = []
            for index in range(count):
                begin, end, _unwind = struct.unpack_from('<III', self.data, section['raw'] + index * 12)
                if begin == 0 or end == 0:
                    continue
                pairs.append((self.image_base + begin, self.image_base + end))
            return sorted(pairs)
        return []

    def function_start(self, va):
        """The start of the function containing va, or None."""
        best = None
        for begin, end in self.pdata_functions():
            if begin <= va < end:
                best = begin
            elif begin > va:
                break
        return best
'''

marker = '''    def frozen_string(self, chars_va):'''
if text.count(marker) != 1:
    raise SystemExit('anchor matched %d times' % text.count(marker))
text = text.replace(marker, helper.rstrip('\n') + '\n\n' + marker, 1)

command = '''    if command == 'func':
        start = image.function_start(address)
        print('%#x -> %s' % (address, ('%#x' % start) if start else 'not in any .pdata function'))
        return 0
'''
anchor = "    if command == 'refs':"
if text.count(anchor) != 1:
    raise SystemExit('command anchor matched %d times' % text.count(anchor))
text = text.replace(anchor, command + '\n' + anchor, 1)

text = text.replace(
    '    python analysis/pe_read_direct.py refs 0x147149A94',
    '    python analysis/pe_read_direct.py refs 0x147149A94\n    python analysis/pe_read_direct.py func 0x140ad5fad')

io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('func command added')
