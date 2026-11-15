import io, re, importlib.util
spec = importlib.util.spec_from_file_location("mc", r"D:\projects\cyber-reverse\replica\tools\mutation-check.py")
mc = importlib.util.module_from_spec(spec); spec.loader.exec_module(mc)
for m in mc.MUTATIONS:
    if 'round 127' in m['name'] or 'round 164' in m['name'] and 'UI' in m['name']:
        print('==', m['name'].replace('—','-'))
        print('   file:', m['file'].replace(r'D:\projects\cyber-reverse\replica', ''))
        print('   find:', repr(m['find'])[:120])
        print('   test:', m.get('test'))
        print('   guard:', m.get('guard'))
