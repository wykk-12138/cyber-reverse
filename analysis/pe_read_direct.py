"""Read the image without IDA: frozen strings and rip-relative references, straight from the file.

WHY THIS EXISTS (the rule in AGENTS §1: say why the public tools are not enough): `analysis/ida.py` needs a live IDA
with the database loaded, and that process has now died four times in this session — always after a heavy publish or
mutation run, which is when memory is tightest. The remaining static work is small and well-defined: read a frozen
`System.String` and find who references it. That does not need a disassembler, and the layout is already established in
this project's own notes:

    [ MethodTable* : 8 bytes ][ Length : 4 bytes ][ UTF-16 chars ... ]
      chars_va - 12

So this reads the PE section table, maps a VA to a file offset, and does both jobs directly. It is deliberately not a
disassembler: `find_disp32` walks every byte of .text and reports the positions where `site_va + 4 + disp32 == target`,
which is exactly the arithmetic the CPU performs for `lea reg, [rip+disp32]`. A hit still has to be confirmed against
the target function's literal set — the R1372 rule — because a byte pattern is not a reference.

Usage:
    python analysis/pe_read_direct.py str 0x147149A94
    python analysis/pe_read_direct.py refs 0x147149A94
    python analysis/pe_read_direct.py func 0x140ad5fad
"""
import io
import struct
import sys

IMAGE = 'target/Cybersole.exe'


class Image:
    """The section table of one PE file, enough to translate and read."""

    def __init__(self, path):
        self.data = io.open(path, 'rb').read()
        pe_offset = struct.unpack_from('<I', self.data, 0x3C)[0]
        if self.data[pe_offset:pe_offset + 4] != b'PE\x00\x00':
            raise SystemExit('not a PE file')

        file_header = pe_offset + 4
        section_count = struct.unpack_from('<H', self.data, file_header + 2)[0]
        optional_size = struct.unpack_from('<H', self.data, file_header + 16)[0]
        optional = file_header + 20
        self.image_base = struct.unpack_from('<Q', self.data, optional + 24)[0]

        self.sections = []
        table = optional + optional_size
        for index in range(section_count):
            entry = table + index * 40
            name = self.data[entry:entry + 8].rstrip(b'\x00').decode('ascii', errors='replace')
            virtual_size, virtual_address, raw_size, raw_pointer = struct.unpack_from(
                '<IIII', self.data, entry + 8)
            self.sections.append({
                'name': name,
                'va': virtual_address,
                'vsize': virtual_size,
                'raw': raw_pointer,
                'raw_size': raw_size,
            })

    def section_of(self, va):
        relative = va - self.image_base
        for section in self.sections:
            if section['va'] <= relative < section['va'] + max(section['vsize'], section['raw_size']):
                return section, relative - section['va']
        return None, None

    def offset_of(self, va):
        section, delta = self.section_of(va)
        if section is None:
            raise SystemExit('address %#x is not in a section' % va)
        return section['raw'] + delta

    def read(self, va, size):
        offset = self.offset_of(va)
        return self.data[offset:offset + size]


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

    def frozen_string(self, chars_va):
        """Read a NativeAOT frozen string: method table, length, UTF-16 characters."""
        header = self.read(chars_va - 12, 12)
        length = struct.unpack_from('<I', header, 8)[0]
        if length > 200000:
            raise SystemExit('implausible length %d at %#x — is that really chars_va?' % (length, chars_va))
        return self.read(chars_va, length * 2).decode('utf-16-le', errors='replace')


def find_disp32(image, target, limit=40):
    """Positions in .text where `site_va + 4 + disp32 == target`."""
    hits = []
    for section in image.sections:
        if not section['name'].startswith('.text'):
            continue
        start = section['raw']
        end = start + min(section['vsize'], section['raw_size']) - 4
        for offset in range(start, end):
            value = struct.unpack_from('<i', image.data, offset)[0]
            site_va = image.image_base + section['va'] + (offset - start)
            if site_va + 4 + value == target:
                hits.append(site_va)
                if len(hits) >= limit:
                    return hits
    return hits


def main(argv):
    if len(argv) < 3:
        raise SystemExit('usage: pe_read_direct.py str|refs <address>')

    image = Image(IMAGE)
    command = argv[1]
    address = int(argv[2], 16)

    if command == 'str':
        print('%#x  %r' % (address, image.frozen_string(address)))
        print('sections: %s' % ', '.join('%s@%#x' % (s['name'], image.image_base + s['va'])
                                         for s in image.sections[:6]))
        return 0

    if command == 'func':
        start = image.function_start(address)
        print('%#x -> %s' % (address, ('%#x' % start) if start else 'not in any .pdata function'))
        return 0

    if command == 'refs':
        for form, label in ((address - 12, 'header'), (address, 'chars')):
            hits = find_disp32(image, form)
            print('%s %#x -> %d site(s)' % (label, form, len(hits)))
            for site in hits[:10]:
                print('    %#x' % site)
        return 0

    raise SystemExit('unknown command %s' % command)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
