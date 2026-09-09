#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def load(name):
    return json.loads((ROOT/'data'/name).read_text(encoding='utf-8'))

manufacturers=load('manufacturers.json')
products=load('products.json')
capabilities=load('capabilities.json')
applications=load('applications.json')

errors=[]

def unique(records, field, label):
    seen={}
    for i,r in enumerate(records):
        value=r.get(field)
        if not value: errors.append(f'{label}[{i}] missing {field}')
        elif value in seen: errors.append(f'duplicate {label} {field}: {value}')
        seen[value]=i

for records,label in [(manufacturers,'manufacturer'),(products,'product'),(capabilities,'capability'),(applications,'application')]:
    unique(records,'id',label); unique(records,'slug',label)

p={x['slug'] for x in products}; c={x['slug'] for x in capabilities}; a={x['slug'] for x in applications}
for m in manufacturers:
    for slug in m.get('products',[]):
        if slug not in p: errors.append(f"{m['slug']}: unknown product {slug}")
    for slug in m.get('capabilities',[]):
        if slug not in c: errors.append(f"{m['slug']}: unknown capability {slug}")
    for slug in m.get('applications',[]):
        if slug not in a: errors.append(f"{m['slug']}: unknown application {slug}")
    if not m.get('evidence'): errors.append(f"{m['slug']}: no evidence")
    for e in m.get('evidence',[]):
        for field in ('claim','source','sourceType','checked','confidence'):
            if not e.get(field): errors.append(f"{m['slug']}: evidence missing {field}")

if errors:
    print('DATA VALIDATION FAILED')
    for e in errors: print(' -',e)
    raise SystemExit(1)
print(f'OK: {len(manufacturers)} manufacturers, {len(products)} products, {len(capabilities)} capabilities, {sum(len(m["evidence"]) for m in manufacturers)} evidence records')
