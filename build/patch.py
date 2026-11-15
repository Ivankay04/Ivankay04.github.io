#!/usr/bin/env python3
# Точечная правка текстов: python3 build/patch.py ru patch.json  ({"a.b.0": значение})
import json, sys, os
R = os.path.dirname(os.path.abspath(__file__))
f = os.path.join(R, 'content', sys.argv[1] + '.json')
c = json.load(open(f, encoding='utf-8'))
for path, v in json.load(open(sys.argv[2], encoding='utf-8')).items():
    d = c; ks = path.split('.')
    for k in ks[:-1]: d = d[int(k)] if isinstance(d, list) else d[k]
    k = ks[-1]
    if isinstance(d, list): d[int(k)] = v
    else: d[k] = v
json.dump(c, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('patched', sys.argv[1])
