import sqlite3


conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()


row = ("Windows 7 x64 Rus", r"d:\Images\Windows 7 x64 Rus\Windows 7 x64 Rus.vmx", "Creo 5.0",
       "Russian", "0", "Creo", "EFD.PRO-")

prod_dirs = ["CFW-2020",
             "CFW-2021",
             "EFD.LAB-2019",
             "EFD.LAB-2020",
             "EFD.NX-2019",
             "EFD.NX-2020",
             "EFD.PRO-2019",
             "EFD.PRO-2020",
             "EFD.SE-2019",
             "EFD.SE-2020",
             "EFD.V5-2019",
             "EFD.V5-2020"]

# cursor.execute("INSERT INTO fenix_maindb(vm_name, vm_path, vm_snap, lang, production, cad, prod_prefix) VALUES (?,?,?,?,?,?,?)", row)

for item in prod_dirs:
    cursor.execute("INSERT INTO prod_dirs (prod_root) VALUES ('%s')" % item)

# cursor.execute("INSERT INTO prod_dirs(prod_root) VALUES (prod_root)", prod_dirs)

#
conn.commit()

# cursor.execute("SELECT vm_name, vm_path, vm_snap, prod_prefix FROM fenix_maindb WHERE production =='1'")
# cursor.execute("SELECT vm_name, vm_path, vm_snap, prod_prefix FROM fenix_maindb WHERE vm_name =='Windows 8 x64 German'")
# cursor.execute("SELECT vm_name, vm_path, vm_snap, prod_prefix FROM fenix_maindb GROUP BY vm_name")

cursor.execute("SELECT prod_root FROM prod_dirs")

# cursor.execute("SELECT vm_name, vm_path, vm_snap, prod_prefix FROM fenix_maindb")

results = cursor.fetchall()
for i in results:
    print(i)


conn.close()


# 33	Windows 10 x64 Turkish	d:\Images\Windows 10 x64 Turkish\Windows 10 x64 Turkish.vmx	SW 2019 SP3.0	Turkish	1	SolidWorks	CFW-

# Windows 7 x64