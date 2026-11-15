import io
src = io.open('pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
for i, ln in enumerate(src, 1):
    if 'GLOBAL_NOT_FN' in ln[12:]:
        print(f'{i:6d} {ln[:170]}')
