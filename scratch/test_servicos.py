import sys
sys.path.insert(0, r'c:\Users\Patrick Ribeiro\Documents\dev\servicoscrc')

import backend.scripts.servicos_organizacao as s

items = s.extract_servicos()
print(f'Total themes: {len(items)}')
if items:
    print(f'First theme: {items[0].name}')
    print(f'Subthemes: {len(items[0].subthemes)}')
    if items[0].subthemes:
        print(f'First subtheme: {items[0].subthemes[0].name}')
        print(f'Services: {len(items[0].subthemes[0].services)}')
else:
    print('NO DATA RETURNED!')
