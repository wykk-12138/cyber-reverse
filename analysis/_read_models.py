import io, re
t = io.open(r'D:\projects\cyber-reverse\replica\src\Cybersole.Core\Models\SmartActions.cs', encoding='utf-8').read()
for name in ('class PublishedTemplate', 'class SmartActionFilterInput', 'class SmartActionFilter', 'class SmartActionStep', 'class SmartActionsDocument'):
    m = re.search(r'public sealed (?:class|record) %s[^\n]*\n\{(.*?)\n\}' % name.split()[-1], t, re.S)
    print('==', name)
    if m:
        body = m.group(1)
        for line in body.split('\n'):
            s = line.strip()
            if s and not s.startswith('//') and ('public' in s or 'internal' in s):
                print('    ', s[:100])
    else:
        print('    (not found)')
