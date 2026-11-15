"""List the contents of a Velopack nupkg and look for a PDB.

R96: the update package is still on disk (Cybersole-5.18.32-win-x64-full.nupkg, 57 MB), and it is a
zip. If it ships a .pdb, IDA can load names and every `sub_140xxxxxx` becomes a real symbol — which
is the one thing the string-level analysis cannot give.
"""
import io
import sys
import zipfile

path = sys.argv[1] if len(sys.argv) > 1 else \
    r"C:\Users\wykk\AppData\Local\Cybersole\packages\Cybersole-5.18.32-win-x64-full.nupkg"

with zipfile.ZipFile(path) as z:
    names = z.namelist()
    print("entries:", len(names))

    pdbs = [n for n in names if n.lower().endswith(".pdb")]
    print("pdb entries:", len(pdbs))
    for n in pdbs[:20]:
        print("  ", n, z.getinfo(n).file_size)

    big = sorted(names, key=lambda n: -z.getinfo(n).file_size)[:12]
    print("\nlargest:")
    for n in big:
        print("  %10d  %s" % (z.getinfo(n).file_size, n))
