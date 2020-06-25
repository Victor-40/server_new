import sqlite3

from pprint import pprint


db_path = r'c:\production_svelte\server\db.sqlite3'
all_cfg_dct = dict()
prod_cfg_dct = dict()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

res = cursor.execute("SELECT vm_name, vm_path, vm_snap, lang, prod_prefix, production, cad FROM fenix_maindb")
all_recs = res.fetchall()

for vm, path, snap, lang, prefix, production, cad in all_recs:
    # print(vm, path, snap, lang, prefix, production, cad)
    if vm in all_cfg_dct:

        all_cfg_dct[vm]['snap'].append(snap)
    else:
        all_cfg_dct[vm] = {'path': path, 'lang': lang, 'snap': [snap]}

for vm, path, snap, lang, prefix, production, cad in all_recs:
    if production == '1':
        if vm in prod_cfg_dct:

            prod_cfg_dct[vm]['snap'].append(snap)
        else:
            prod_cfg_dct[vm] = {'path': path, 'lang': lang, 'snap': [snap]}


pprint(all_cfg_dct)
pprint(prod_cfg_dct)
