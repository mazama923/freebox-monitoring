import os
import time
from dotenv import load_dotenv
from prometheus_client import start_http_server, Gauge, Info
from api_request import get_request

existing_metrics = {}

def start_prometheus():
    load_dotenv()
    start_http_server(int(os.getenv("PORT_HTTP")))

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

def time_script(start_time):
    time_script = get_or_create_gauge('freebox_time_script', 'Metrics generation time')
    end_time = time.time()
    duration = end_time - start_time
    formatted_duration = "{:.2f}".format(duration)
    time_script.set(formatted_duration)

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

def lan_config(headers):
    lan_config_request = get_request("lan/config/", headers=headers)
    name_dns = lan_config_request['result']['name_dns']
    name_mdns = lan_config_request['result']['name_mdns']
    name = lan_config_request['result']['name']
    mode = lan_config_request['result']['mode']
    name_netbios = lan_config_request['result']['name_netbios']
    ip = lan_config_request['result']['ip']
    lan_config = get_or_create_gauge('freebox_lan_config', 'Lan config', ['name_dns', 'name_mdns', 'name', 'mode', 'name_netbios', 'ip'])
    lan_config.labels(name_dns=name_dns, name_mdns=name_mdns, name=name, mode=mode, name_netbios=name_netbios, ip=ip)

def port_forwarding(headers):
    port_forwarding_request = get_request("fw/redir/", headers=headers)
    if 'result' in port_forwarding_request and port_forwarding_request['success']:
        for item in port_forwarding_request['result']:
            id = item.get('id', '')
            enabled = item.get('enabled', '')
            ip_proto = item.get('ip_proto', '')
            wan_port_start = item.get('wan_port_start', '')
            wan_port_end = item.get('wan_port_end', '')
            lan_ip = item.get('lan_ip', '')
            lan_port = item.get('lan_port', '')
            hostname = item.get('hostname', '')
            host = item.get('host', '')
            src_ip = item.get('src_ip', '')
            comment = item.get('comment', '')
            port_forwarding = get_or_create_gauge('freebox_port_forwarding', 'Port forwarding', ['id', 'enabled', 'ip_proto', 'wan_port_start', 'wan_port_end', 'lan_ip', 'lan_port', 'hostname', 'host', 'src_ip', 'comment'])
            port_forwarding.labels(id=id, enabled=str(enabled), ip_proto=enumerate(ip_proto), wan_port_start=str(wan_port_start), wan_port_end=wan_port_end, lan_ip=str(lan_ip), lan_port=lan_port, hostname=str(hostname), host=host, src_ip=str(src_ip), comment=str(comment)).set(1 if enabled else 0)
    else:
        print("No port forwarding rules found.")

def port_incoming(headers):
    port_incoming_request = get_request("fw/incoming/", headers=headers)
    for item in port_incoming_request['result']:
        id = item['id']
        enabled = item['enabled']
        type = item['type']
        active = item['active']
        max_port = item['max_port']
        min_port = item['min_port']
        in_port = item['in_port']
        readonly = item['readonly']
        netns = item['netns']
        port_incoming = get_or_create_gauge('freebox_port_incoming', 'Port incoming', ['id', 'enabled', 'type', 'active', 'max_port', 'min_port', 'in_port', 'readonly', 'netns'])
        port_incoming.labels(id=id, type=type, enabled=str(enabled), active=str(active), max_port=max_port, min_port=min_port, in_port=in_port, readonly=str(readonly), netns=netns).set(1 if enabled else 0)

def vpn_connection(headers):
    vpn_connection_request = get_request("vpn/connection/", headers=headers)
    if 'result' in vpn_connection_request and vpn_connection_request['success']:
        for item in vpn_connection_request['result']:
            rx_bytes = item['rx_bytes']
            tx_bytes = item['tx_bytes']
            user = item['user']
            vpn = item['vpn']
            src_port = item['src_port']
            src_ip = item['src_ip']
            auth_time = item['auth_time']
            local_ip = item['local_ip']
        vpn_connection = get_or_create_gauge('freebox_vpn_connection', 'User connect to VPN', ['rx_bytes', 'tx_bytes', 'user', 'vpn', 'src_port', 'src_ip', 'auth_time', 'local_ip'])                     
        vpn_connection.labels(rx_bytes=rx_bytes, tx_bytes=tx_bytes, user=user, vpn=vpn, src_port=src_port, src_ip=src_ip, auth_time=auth_time, local_ip=local_ip)
    else:
        print("No user connect to VPN.")