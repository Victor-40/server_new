import json
import os
import sqlite3
import re
import sys
import win32com.client as win32


def get_dirlist() -> list:
    with open('cfg/dir_list.json') as fi:
        prod_dct = json.load(fi)

    search_dirs = [os.path.join(root_path, item) for item in prod_dct['prod_dirs']]
    _all_list = list()
    for _dir in search_dirs:
        root_obj = os.scandir(_dir)
        for item in root_obj:
            _all_list.append(item.path)
    return _all_list


def find_prefix(_pth: str) -> str:
    patt = re.compile(r'[^-]*-', re.I)
    _matches = re.match(patt, os.path.basename(_pth))
    if not _matches:
        print('error matching prefix')
        sys.exit(1)
    return _matches.group(0)



root_script = os.getcwd()
q1 = 'CFW-2020PR-4696_x64__git--efd_dev.4696_07.08.2019_1'

patt = re.compile(r'.*-(\d\d\d\d)(_x64)?__(.*$)')

m = re.search(patt, q1)
# for i in range(4):
#     print(m.group(i))

build_number = m.group(1)
label = m.group(3)

print('build_number=', build_number)
print('label=', label)
str_search = r'.*-%s(_x64)?__%s' % (build_number, label)
pattern = re.compile(str_search, re.I)

#########  db  ##############

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()


cursor.execute("SELECT vm_name, vm_path, vm_snap, prod_prefix FROM fenix_maindb WHERE production =='1'")

results = cursor.fetchall()
# for i in results:
#     print(i)

conn.close()
##########

root_path = r'\\svr-rum-net-04\new_versions'

all_lst = get_dirlist()

setup_lst = list()
for i in all_lst:
    mm = re.search(pattern, i)
    if mm:
        setup_lst.append(mm.group(0))

result_lst = list()
for setup_path in setup_lst:
    # print(setup_path)
    curr_prefix = find_prefix(setup_path)

    for j in results:
        vm_name, vm_path, snapshot_name, prefix = j
        if prefix == curr_prefix:
            result_lst.append([setup_path, vm_name, vm_path, snapshot_name, '0'])
    # break

##### Excel ################

wb_path = os.path.join(root_script, 'VM-Monitor.Jobs.xls')
if os.path.exists(wb_path):
    os.remove(wb_path)

excel = win32.gencache.EnsureDispatch('Excel.Application')
wb = excel.Workbooks.Add()
ws = wb.Worksheets.Add()
ws.Name = "Table"

# write table headers
ws.Cells(1, 1).Value = "InstallPath"
ws.Cells(1, 2).Value = "Name"
ws.Cells(1, 3).Value = "Path"
ws.Cells(1, 4).Value = "SnapName"
ws.Cells(1, 5).Value = "Done"

for i in range(len(result_lst)):
    for j in range(5):
        ws.Cells(i + 2, j + 1).Value = result_lst[i][j]

wb.SaveAs(wb_path, 56)
excel.Application.Quit()
