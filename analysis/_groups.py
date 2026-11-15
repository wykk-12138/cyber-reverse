import io
pool = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read()
for s in ['Nike GS','Footlocker (Asia)','Demandware (Funko)','Popmart','Warhammer','Search stores','Add a group to get started']:
    print('%-28s %s' % (s, 'IN POOL' if s in pool else '-'))
