"""Write the payment-shaped names the replica never mentions, as a work queue rather than a verdict.

The keyword filter is a heuristic and its false positives are named in the file header, because R1223 showed what
happens when a name-shape rule is treated as a classification. What the list does support is the negative fact it
states: these names occur in the image's method table and appear nowhere in replica/src.

Usage:
    python analysis/payment_name_gaps.py
"""
import glob
import io
import json
import re

KEYWORDS = r'Stripe|PayPal|Adyen|Square|Unzer|ThreeDs|3Ds|Cardinal|Intent|Mandate|Card|Payment|Checkout|Order|Cart|Shipping|Address'


def main():
    data = json.load(io.open('analysis/state_machine_names.json', encoding='utf-8'))
    names = data['names']

    table_re = re.compile(r'new Step\("(\w+)",\s*(\d+)\)')
    table = set()
    for path in glob.glob('replica/src/**/*Step*.cs', recursive=True):
        text = io.open(path, encoding='utf-8', errors='replace').read()
        table |= {m.group(1) for m in table_re.finditer(text)}

    src = {}
    for path in glob.glob('replica/src/**/*.cs', recursive=True):
        try:
            src[path] = io.open(path, encoding='utf-8', errors='replace').read()
        except OSError:
            pass

    pat = re.compile(KEYWORDS, re.I)
    candidates = sorted(n for n in set(names) - table if pat.search(n))
    absent = [n for n in candidates
              if not any(re.search(r'\b' + re.escape(n) + r'\b', t) for t in src.values())]

    out = 'analysis/payment_name_gaps.txt'
    with io.open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write('# Payment-shaped method names from analysis/state_machine_names.json (image method table).\n')
        f.write('# Section 1: not named by any new Step(...) in replica/src.\n')
        f.write('# Section 2: additionally, no occurrence anywhere under replica/src.\n')
        f.write('#\n')
        f.write('# THE FILTER IS A KEYWORD HEURISTIC, NOT A CLASSIFICATION. Known false positives:\n')
        f.write('#   DetectByteOrderMarkAsync   matched "Order" inside "ByteOrder"\n')
        f.write('#   FormatIPv6Address          matched "Address" inside an IPv6 formatter\n')
        f.write('#   DragBorderPressed          matched "Order" inside "Border"\n')
        f.write('# So a row here means "worth reading", not "missing feature".\n')
        f.write('# Regenerate with: python analysis/payment_name_gaps.py\n\n')
        f.write('# SECTION 1 - not in the step tables (%d)\n' % len(candidates))
        for n in candidates:
            f.write('%s\t%#x\n' % (n, names[n]))
        f.write('\n# SECTION 2 - and absent from replica/src entirely (%d)\n' % len(absent))
        for n in absent:
            f.write('%s\t%#x\n' % (n, names[n]))

    print('keyword-shaped and not in the step tables: %d' % len(candidates))
    print('of those, absent from replica/src entirely: %d' % len(absent))
    print('wrote', out)


if __name__ == '__main__':
    main()
