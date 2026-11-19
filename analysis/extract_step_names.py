"""Extract the compiler-generated state-machine method names from a window of the image's name table.

The names are packed ASCII with length prefixes, not frozen UTF-16 strings, so this scans printable ASCII runs and
keeps those that match the compiler's shapes (`<Method>d__N`, `<Method>b__N_M`, `<Method>g__Local|N_M`).

Coverage matters more than completeness here: a name found is proof the image has it, a name missing from the
window proves nothing until the window is known to cover the whole table, so the output always reports the window.
"""
import io
import json
import re
import subprocess
import sys

START = int(sys.argv[1], 16) if len(sys.argv) > 1 else 0x143370000
SIZE = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0x40000
OUT = sys.argv[3] if len(sys.argv) > 3 else 'analysis/state_machine_names.txt'

code = "import ida_bytes; d = ida_bytes.get_bytes(%d, %d); print(d.hex() if d else '')" % (START, SIZE)
out = subprocess.run([sys.executable, 'analysis/ida.py', 'py', code, '--timeout', '900'],
                     capture_output=True, text=True, encoding='utf-8', errors='replace')
doc = json.JSONDecoder().raw_decode(out.stdout)[0]
blob = bytes.fromhex((doc.get('stdout') or '').strip().split('\n')[-1])
print('read %d bytes from %#x' % (len(blob), START))

METHOD = re.compile(r'<([A-Za-z_]\w*)>(?:d__\d+|b__\d+_\d+|g__\w+\|\d+_\d+)')
names = {}
run = bytearray()
run_start = 0
for idx, byte in enumerate(blob + b'\x00'):
    if 0x20 <= byte < 0x7f:
        if not run:
            run_start = idx
        run.append(byte)
    else:
        if len(run) >= 8:
            text = run.decode('ascii')
            for m in METHOD.finditer(text):
                names.setdefault(m.group(1), START + run_start)
        run = bytearray()

print('distinct method names: %d' % len(names))
with io.open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    f.write('# window %#x..%#x (%d bytes)\n' % (START, START + SIZE, SIZE))
    for name in sorted(names):
        f.write('%s\t%#x\n' % (name, names[name]))
print('wrote', OUT)
