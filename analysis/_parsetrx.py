import xml.etree.ElementTree as ET
p = r'D:\projects\cyber-reverse\analysis\_mutation-restore.trx'
NS = '{http://microsoft.com/schemas/VisualStudio/TeamTest/2010}'
root = ET.parse(p).getroot()
for r in root.iter(NS + 'UnitTestResult'):
    if r.get('outcome') == 'Failed':
        print('FAILED:', r.get('testName'), ' duration=', r.get('duration'))
        out = r.find(NS + 'Output')
        if out is not None:
            err = out.find(NS + 'ErrorInfo')
            if err is not None:
                msg = err.findtext(NS + 'Message') or ''
                st = err.findtext(NS + 'StackTrace') or ''
                print('  msg:', ' | '.join(msg.strip().splitlines()[:4]))
                print('  stk:', ' | '.join(st.strip().splitlines()[:6]))
