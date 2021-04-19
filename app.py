from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import re
import vix
import subprocess
import sys
from win32com import client
import pythoncom
import time


# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/api/*': {'origins': '*'}})
# CORS(app)

root_nv = r'\\svr-rum-net-04\new_versions'
root_host_test = r'e:\Testing\Test-1'
root_guest_test = r'c:\Test'
root_report = r'\\rum-cherezov-dt\!Reports'
job_file = r'e:\Testing_JS\VMWare.JS\VM-Monitor.Jobs.xls'

all_cfg_dct = dict()

with open(r'c:\production_svelte\server_new\cfg\main_db.json') as fi:
    origin = json.load(fi)

for key in origin:
    snaplist = origin[key]['snaplist']
    new_snaplist = [i['snap'] for i in snaplist if i['show'] == 1]
    all_cfg_dct[key] = {'lang': origin[key]['lang'],
                        'path': origin[key]['path'],
                        'snap': sorted(new_snaplist)}

production_lst = list()

for key in origin:
    for item in origin[key]['snaplist']:
        if item['production'] == 1:
            row_obj = {'vm': key,
                       'lang': origin[key]['lang'],
                       'path': origin[key]['path'],
                       'winver': origin[key]['winver'],
                       'snaplist': item}
            production_lst.append(row_obj)

# pprint.pprint(production_lst)

with open(r'cfg\prod_dirs.json') as fi:
    all_prod_dirs = json.load(fi)

##############################  end mongo  ##########################################

host = vix.VixHost(service_provider=3)


def find_builds(_dirname, _prod, subdir, _vs2019):
    pattern_in = re.compile(r'.*-(\d{4})(?:_x64)*__(.*)$', re.I)
    matches = re.search(pattern_in, _dirname)
    build = matches.group(1)
    tag = matches.group(2)
    # print(build, tag)

    pattern_out = re.compile(r'-%s(?:_x64)*__*%s$' % (build, tag), re.I)

    work_prod = list()
    for i in _prod:
        for prod_dir in all_prod_dirs:
            if prod_dir.startswith(i):
                work_prod.append(prod_dir)

    # vs2019 only
    if _vs2019:
        work_prod = ["vs2019_" + x for x in work_prod]

    search_dirs = [os.path.join(root_nv, item, subdir) for item in work_prod]
    setups = list()

    for _dir in search_dirs:
        if os.path.exists(_dir):
            obj = os.scandir(_dir)
            for item in obj:
                if re.search(pattern_out, item.name):
                    setups.append(item.path)
    return setups


def make_xls(params):
    # print("params", params)
    setups = params['setups']
    result = list()

    for _setup in setups:
        setup_prefix = os.path.basename(_setup).split('-')[0] + '-'

        selected = [item for item in production_lst if item['snaplist']['prefix'] == setup_prefix]
        selected = [item for item in selected if item['lang'] in params['lang']]
        selected = [item for item in selected if item['winver'] in params["win"]]

        for item in selected:
            result.append((_setup,  item['vm'], item['path'],  item['snaplist']['snap'], '0'))

    if os.path.exists(job_file):
        os.remove(job_file)
    pythoncom.CoInitialize()
    xls = client.Dispatch("Excel.Application")

    wb = xls.Workbooks.Add()
    sheet = wb.WorkSheets("Sheet1")
    sheet.Name = "Table"

    # header
    header_list = ["InstallPath", "Name", "Path", "SnapName", "Done"]
    for i in range(len(header_list)):
        sheet.Cells(1, i + 1).value = header_list[i]

    for i in range(len(result)):
        for j in range(5):
            sheet.Cells(i + 2, j + 1).value = result[i][j]

    wb.SaveAs(job_file, 56)
    wb.Close()
    pythoncom.CoUninitialize()

    # make info-file

    root_path = r'e:\testing\test'
    os.chdir(root_path)
    new_info = params['report']
    if new_info:
        new_info_name = new_info + '.info'
        for item in os.scandir():
            if item.name.endswith('.info'):
                os.remove(item.name)

        open(new_info_name, 'a').close()

    return result


# sanity check route
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!'), 202


@app.route('/api/cfg', methods=['GET'])
def find_busy():
    with open(r'c:\production_svelte\server_new\cfg\busy_vm.json') as fi:
        busy_list = json.load(fi)

    cfg = dict()

    for _vm in all_cfg_dct:
        cfg[_vm] = {'path': all_cfg_dct[_vm]['path'], 'snap': all_cfg_dct[_vm]['snap']}

    for _vm in cfg:
        try:
            vm = host.open_vm(cfg[_vm]['path'])
        except vix.VixError as e:
            print(e)
            print(cfg[_vm]['path'])
            sys.exit(1)
        if _vm in busy_list:
            cfg[_vm]['status'] = 'busy'
            continue
        if vm.is_running:
            cfg[_vm]['status'] = 'busy'
        else:
            cfg[_vm]['status'] = 'free'

    return jsonify(cfg)


@app.route('/api/findsetups', methods=['GET', 'POST'])
def find_setups():
    if request.method == 'POST':
        post_data = request.get_json()
        # print("find-setups", post_data)
        response_object = find_builds(post_data['dirname'], post_data['products'], post_data['subdir'],
                                      post_data['vs2019'])
    else:
        response_object = ['get']

    return jsonify(response_object)


@app.route('/api/makexls', methods=['POST'])
def makexls():
    post_data = request.get_json()
    # print('request', post_data)
    response_object = make_xls(post_data)

    return jsonify(response_object)


@app.route('/api/startclear', methods=['POST'])
def start_clear():
    post_data = request.get_json()
    # print(post_data)

    vm_name = post_data['vm']
    vm_path = all_cfg_dct[vm_name]['path']
    snapshot = post_data['snap']

    vm = host.open_vm(vm_path)
    if vm.is_running:
        return jsonify("ERROR: VM %s is already running" % vm_name)
    work_snapshot = vm.snapshot_get_named(snapshot)
    vm.snapshot_revert(work_snapshot)
    time.sleep(1)
    vm.power_on(launch_gui=True)

    return jsonify("VM %s was started" % vm_name)


@app.route('/api/allcfg', methods=['GET'])
def all_cfg():
    return jsonify(all_cfg_dct)


@app.route('/api/start_testset', methods=['GET'])
def start_testset():
    subprocess.call([r'e:\Testing\VMWare\start_auto.bat'])
    return jsonify('OK! Testset started')


if __name__ == '__main__':
    app.run()
