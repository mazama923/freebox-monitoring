import os
from dotenv import load_dotenv
from prometheus_client import start_http_server, Gauge, Info
from api_request import get_request

existing_metrics = {}


def start_prometheus():
    load_dotenv()
    start_http_server(8000)


def get_or_create_gauge(name, description, labelnames=[]):
    if name not in existing_metrics:
        gauge = Gauge(name, description, labelnames=labelnames)
        existing_metrics[name] = gauge
    else:
        gauge = existing_metrics[name]
    return gauge


def get_or_create_info(name, description):
    if name not in existing_metrics:
        info_metric = Info(name, description)
        existing_metrics[name] = info_metric
    else:
        info_metric = existing_metrics[name]
    return info_metric


def system_metrics(headers):
    system_request = get_request("system/", headers=headers)

    temp_t1 = system_request['result']['sensors'][1]['value']
    temp_t2 = system_request['result']['sensors'][0]['value']
    temp_t3 = system_request['result']['sensors'][2]['value']
    temp_cpu_cp_master = system_request['result']['sensors'][3]['value']
    temp_cpu_ap = system_request['result']['sensors'][4]['value']
    temp_cpu_cp_slave = system_request['result']['sensors'][5]['value']
    temp = get_or_create_gauge('freebox_temperature', 'Température', labelnames=['temp_t1', 'temp_t2', 'temp_t3', 'temp_cpu_cp_master', 'temp_cpu_ap', 'temp_cpu_cp_slave'])
    temp.labels(temp_t1=temp_t1, temp_t2=temp_t2,temp_t3=temp_t3,temp_cpu_cp_master=temp_cpu_cp_master,temp_cpu_ap=temp_cpu_ap,temp_cpu_cp_slave=temp_cpu_cp_slave)

    fan0_speed = system_request['result']['fans'][1]['value']
    fan1_speed = system_request['result']['fans'][0]['value']
    fans = get_or_create_gauge('freebox_fan_speed', 'Ventilateur', labelnames=['fan0_speed', 'fan1_speed'])
    fans.labels(fan0_speed=fan0_speed,fan1_speed=fan1_speed)

    firmware_version = get_or_create_info(
        'freebox_firmware_version', 'Firmware version')
    firmware_version.info(
        {'version': system_request['result']['firmware_version']})

    start_from = get_or_create_gauge('freebox_start_from', 'uptime_val')
    start_from.set(system_request['result']['uptime_val'])


def lan_browser_pub_metrics(headers):
    lan_browser_pub_request = get_request("lan/browser/pub/", headers=headers)
    for item in lan_browser_pub_request['result']:
        mac_address = item['l2ident']['id']
        vendor_name = item['vendor_name']
        host_type = item['host_type']   
        last_time_reachable = item['last_time_reachable']
        ip = item['l3connectivities'][0]['addr']
        reachable = item.get('reachable', False)
        last_activity = item['last_activity']
        access_point = item.get('access_point', '')
        default_name = item['default_name']
        first_activity = item['first_activity']
        primary_name = item['primary_name']

        lan_browser_pub = get_or_create_gauge('freebox_lan_browser_pub', 'Lan browser pub', ['mac_address', 'vendor_name', 'host_type', 'last_time_reachable', 'ip', 'last_activity', 'access_point', 'default_name', 'first_activity', 'primary_name'])

        lan_browser_pub.labels(mac_address=mac_address,vendor_name=vendor_name,host_type=host_type,last_time_reachable=last_time_reachable,ip=ip,last_activity=last_activity,access_point=access_point,default_name=default_name,first_activity=first_activity,primary_name=primary_name).set(1 if reachable else 0)
