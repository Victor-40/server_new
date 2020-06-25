import pprint
import sqlite3


db_path = r'c:\production_svelte\server\db.sqlite3'

########### DB ##################

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

res = cursor.execute("SELECT vm_name,  vm_snap, lang  FROM fenix_maindb")
all_snapshots = res.fetchall()


my_dict = dict()

for item in all_snapshots:
    # print(item)
    vm, snap, lang = item
    # print(vm, snap)
    if vm in my_dict:
        my_dict[vm]['snap'].append(snap)
    else:
        my_dict[vm] = {'snap': [snap], 'lang': lang}
        # pprint.pprint(my_dict)

for item in my_dict:
    my_dict[item]['snap'] = sorted(my_dict[item]['snap'])

pprint.pprint(my_dict)
