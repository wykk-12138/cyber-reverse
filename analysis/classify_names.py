"""Partition the image's method-name set into framework-shaped and business-shaped buckets by name prefix.

This is a heuristic and is labelled as one: a name whose type prefix belongs to a known library (System, Avalonia,
Newtonsoft, Grpc, MySql, ...) is counted as framework-shaped; everything else is business-shaped. The split is a
starting point for reading, not a verdict about what any function does - R730 already recorded what happens when a
name-prefix rule is treated as a classifier of behaviour.

Usage:
    python analysis/classify_names.py
"""
import io
import json
import re

FRAMEWORK = (
    'System', 'Avalonia', 'Newtonsoft', 'Microsoft', 'Google', 'Grpc', 'Proto', 'MySql', 'Sqlite',
    'Skia', 'HarfBuzz', 'HarfBuzzSharp', 'SharpZipLib', 'Brotli', 'Zstd', 'Lz4', 'Tls', 'Ssl',
    'Http', 'Sockets', 'Dns', 'Ping', 'File', 'Directory', 'Path', 'Encoding', 'Crypto', 'X509',
    'Dictionary', 'Enumerable', 'List', 'Array', 'Span', 'Memory', 'Task', 'Async', 'ValueTask',
    'Regex', 'Json', 'String', 'Char', 'Byte', 'Int', 'Double', 'Decimal', 'DateTime', 'TimeSpan',
    'Guid', 'Uri', 'Convert', 'Math', 'Buffer', 'Stream', 'Reader', 'Writer', 'Builder', 'Comparer',
    'Equality', 'Interlocked', 'Monitor', 'Thread', 'Timer', 'Cancellation', 'Exception', 'Debug',
    'Trace', 'Console', 'Object', 'Type', 'Reflection', 'Runtime', 'Activator', 'Delegate',
    'DependencyInjection', 'Logging', 'Options', 'Configuration', 'Hosting', 'Channels', 'Pipelines',
    'Diagnostics', 'Net', 'Security', 'Text', 'Globalization', 'Collections', 'Linq', 'Numerics',
)


def main():
    data = json.load(io.open('analysis/state_machine_names.json', encoding='utf-8'))
    names = data['names']

    table_names = set()
    table_re = re.compile(r'new Step\("(\w+)",\s*(\d+)\)')
    import glob
    for path in glob.glob('replica/src/**/*Step*.cs', recursive=True):
        text = io.open(path, encoding='utf-8', errors='replace').read()
        table_names |= {m.group(1) for m in table_re.finditer(text)}

    unlisted = sorted(set(names) - table_names)
    framework = [n for n in unlisted if n.startswith(FRAMEWORK)]
    business = [n for n in unlisted if not n.startswith(FRAMEWORK)]

    print('image names: %d   replica table names: %d   unlisted: %d'
          % (len(names), len(table_names), len(unlisted)))
    print('framework-shaped (prefix in the library list): %d' % len(framework))
    print('business-shaped (everything else):             %d' % len(business))

    groups = {}
    for n in business:
        m = re.match(r'(Get|Set|Submit|Start|Create|Add|Find|Resolve|Handle|Complete|Confirm|Validate|Run|'
                     r'Continue|Apply|Build|Check|Clear|Save|Load|Fetch|Update|Delete|Remove|Send|Read|'
                     r'Parse|Login|Authorize|Monitor|Draw|Buy|Checkout|Pay|Capture|Init)\w*', n)
        key = m.group(1) if m else '(other)'
        groups.setdefault(key, []).append(n)
    print('\nbusiness-shaped by leading verb:')
    for key in sorted(groups, key=lambda k: -len(groups[k])):
        print('  %-12s %4d   e.g. %s' % (key, len(groups[key]), ', '.join(sorted(groups[key])[:4])))

    with io.open('analysis/state_machine_names_business.txt', 'w', encoding='utf-8', newline='\n') as f:
        for n in sorted(business):
            f.write('%s\t%#x\n' % (n, names[n]))
    print('\nwrote analysis/state_machine_names_business.txt (%d names)' % len(business))


if __name__ == '__main__':
    main()
