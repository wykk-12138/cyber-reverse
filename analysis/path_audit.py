"""Classify path-shaped literals against the full IDA string dump, in four buckets.

Local and complete: analysis/ida_strings.txt is every string IDA knows (324,901 rows), not the pool sample R816 warned
about, so a lookup here answers "is this literal attested" for the whole image without one round trip per literal.

Buckets, and why each is separate (this is the lesson of R1247, where five misses reduced to one):
  exact          the literal appears as a substring of some string in the image
  prefix-only    it does not, but its path part (up to any '?') does -- the query is assembled from fragments
  prose          the literal's source line is a message, not a request: a regex happily lifts a path out of prose
  no-hit         none of the above; this is the only bucket that deserves the word gap

Usage:
    python analysis/path_audit.py "replica/src/Cybersole.Stores/Payments/*.cs"
    python analysis/path_audit.py "replica/src/Cybersole.Stores/Flows/*.cs" analysis/flow_path_audit.txt
"""
import glob
import io
import re
import sys

PATH_LITERAL = re.compile(r'"((?:/[a-z0-9]|[a-z0-9]+/)[^"\\]{3,})"', re.I)


def load_strings(path='analysis/ida_strings.txt'):
    rows = []
    for line in io.open(path, encoding='utf-8', errors='replace'):
        tab = line.find('\t')
        if tab > 0:
            rows.append(line[tab + 1:].rstrip('\n'))
    return rows


def main(argv):
    pattern = argv[0] if argv else 'replica/src/Cybersole.Stores/Payments/*.cs'
    out_path = argv[1] if len(argv) > 1 else 'analysis/path_audit.txt'
    strings = load_strings()
    blob = '\n'.join(strings)

    literals = {}
    for path in glob.glob(pattern):
        name = path.replace('\\', '/').split('/')[-1]
        raw = io.open(path, encoding='utf-8', errors='replace').read()
        for line in raw.split('\n'):
            stripped = line.lstrip()
            for m in PATH_LITERAL.finditer(line):
                lit = m.group(1)
                if len(lit) < 6:
                    continue
                is_prose = stripped.startswith('//') or ' ' in lit
                literals.setdefault(lit, (name, is_prose))

    buckets = {'exact': [], 'prefix-only': [], 'assembled': [], 'pattern': [], 'prose': [], 'no-hit': []}
    for lit, (src, is_prose) in sorted(literals.items()):
        if is_prose:
            buckets['prose'].append((lit, src))
        elif '{' in lit:
            # R1248: /api/v1/carts/{c.Session.CartId} is not a literal the code sends; it is a template whose parts
            # are concatenated, so the image would hold the fixed prefix only. Counting these as gaps inflated the
            # no-hit bucket from 31 to something meaningless.
            buckets['assembled'].append((lit, src))
        elif re.search(r'\(\?|\[\^|\[\w|\\d|\.\*|\+\)', lit):
            buckets['pattern'].append((lit, src))
        elif lit in blob:
            buckets['exact'].append((lit, src))
        elif lit.split('?')[0] in blob:
            buckets['prefix-only'].append((lit, src))
        else:
            buckets['no-hit'].append((lit, src))

    print('literals: %d  (%s)' % (len(literals), pattern))
    for k in ('exact', 'prefix-only', 'assembled', 'pattern', 'prose', 'no-hit'):
        print('  %-12s %4d' % (k, len(buckets[k])))

    with io.open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('# Path-shaped literals from %s, classified against analysis/ida_strings.txt (full IDA list).\n' % pattern)
        f.write('# exact       literal appears in the image\n')
        f.write('# prefix-only literal does not, but its path up to "?" does -- the query is a separate fragment\n')
        f.write('# prose       the source line is a comment or the literal contains spaces: not a request\n')
        f.write('# no-hit      none of the above -- the only bucket that is a candidate gap\n')
        f.write('# Regenerate with: python analysis/path_audit.py "%s" %s\n\n' % (pattern, out_path))
        for k in ('no-hit', 'prefix-only', 'exact', 'prose'):
            f.write('# %s (%d)\n' % (k.upper(), len(buckets[k])))
            for lit, src in buckets[k]:
                f.write('%-58s\t%s\n' % (lit, src))
            f.write('\n')

    print('\nno-hit detail:')
    for lit, src in buckets['no-hit'][:30]:
        print('   %-48s %s' % (lit[:48], src))
    print('\nwrote', out_path)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
