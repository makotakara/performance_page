from flask import Flask, render_template
import os
import re
import datetime

app = Flask(__name__)

@app.route('/')
def index():

    metrics = os.popen("curl -s http://127.0.0.1:9100/metrics | grep -v '#'").read().split('\n')

    dict_tmp = {}

    for metric in metrics:
        match_1 = re.search(r'node_time_seconds|node_boot_time_seconds|node_load|node_memory_MemAvailable_bytes|node_memory_MemTotal_bytes|node_memory_SwapFree_bytes|node_memory_SwapTotal_bytes', metric)
        
        if match_1:
            key, value = metric.split()
            dict_tmp[key]=value

        match_2 = re.search(r'node_filesystem_avail_bytes.*mountpoint="/"', metric)

        if match_2:
            key, value = metric.split()
            dict_tmp["fs_avail"]=value

        match_3 = re.search(r'node_filesystem_size_bytes.*mountpoint="/"', metric)

        if match_3:
            key, value = metric.split()
            dict_tmp["fs_size"]=value

    perf = {}

    uptime = (float(dict_tmp["node_time_seconds"]) - float(dict_tmp["node_boot_time_seconds"]))
    uptime = datetime.timedelta(seconds=int(uptime))

    la1  = dict_tmp["node_load1"]
    la5  = dict_tmp["node_load5"]
    la15 = dict_tmp["node_load15"]

    memory_util = (1 - float(dict_tmp["node_memory_MemAvailable_bytes"]) / float(dict_tmp["node_memory_MemTotal_bytes"])) * 100
    memory_util = round(memory_util, 2)

    swap_util  = 100 - (100 * float(dict_tmp["node_memory_SwapFree_bytes"]) / float(dict_tmp["node_memory_SwapTotal_bytes"]) )
    swap_util  = round(swap_util, 2)

    fs_util = 100 - (float(dict_tmp["fs_avail"]) * 100 / float(dict_tmp["fs_size"]))
    fs_util = round(fs_util, 2)

    perf["uptime"]=uptime
    perf["la1"]=la1
    perf["la5"]=la5
    perf["la15"]=la15
    perf["memory_util"]=memory_util
    perf["swap_util"]=swap_util
    perf["fs_util"]=fs_util

    return render_template('index.html', perf=perf)
