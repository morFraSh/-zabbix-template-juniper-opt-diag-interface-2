#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from jnpr.junos import Device
import jnpr.junos.exception
from pprint import pprint
from lxml import etree
from lxml import html
import jxmlease
import argparse
import re
import timeit
import json
from pyzabbix.api import ZabbixAPI, ZabbixAPIException

#timer_A = timeit.default_timer()

parser = argparse.ArgumentParser(description='Get information on optical trancievers', \
                                 usage='zabbiname host user key timeout (interface name)' )

parser.add_argument('user', help='username')
parser.add_argument('key', help='full path to rsa private key')
parser.add_argument('host', help='set host address')
parser.add_argument('zabbiname', help='set host name zabbix')
parser.add_argument('timeout', help='set host timeout')

args = parser.parse_args()

dev = Device(host=args.host, user=args.user, ssh_private_key_file=args.key, gather_facts=False)

dev.open()

ddm_interfaces = dev.rpc.get_interface_optics_diagnostics_information()
ddm_interfaces = ddm_interfaces.xpath('//name')

dev.close()

macro_str = ""

#macro_elem_list

for interface in ddm_interfaces:
    data = jxmlease.parse(etree.tostring(interface,encoding = 'unicode'))
    for key in data:
        macro_str = str(data[key]) + '|' + macro_str

macro_str=macro_str[:-1]
macro_str='('+ macro_str + ')'
macro_value = macro_str

macro_name = '{$DIAG_OPT_FILTER}'
zabi_host_name = args.zabbiname


zapi = ZabbixAPI('http://10.11.0.1/zabbix',user="<user>",password='<password>')


hostname_get = zapi.host.get(output=['hostid'],filter={"host":zabi_host_name})

for host in hostname_get:
    hostid_zabbi = host['hostid']

macroget_zapi = zapi.usermacro.get(output=['hostid','hostmacroid','macro'],hostids=hostid_zabbi,filter={'macro': macro_name})

try:
    if macroget_zapi == []:
       # print('Net')
        macrocrete = zapi.usermacro.create(hostid=hostid_zabbi, macro=macro_name, value=macro_value)
       # print(macrocrete)
    else:
        #print(macroget_zapi)
        for id in macroget_zapi:
            macro_id = id['hostmacroid']
           # print(macro_id)
        macroupdate_zapi = zapi.usermacro.update(hostmacroid = macro_id, value = macro_value)
        #print(macroupdate_zapi)

except ZabbixAPIException as e:
    print(e)
    sys.exit()

#print(timeit.default_timer()-timer_A)
