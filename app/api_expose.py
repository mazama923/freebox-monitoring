import os
import time
from dotenv import load_dotenv
from prometheus_client import start_http_server, Gauge, Info
from api_request import get_request, post_with_headers_request
import concurrent.futures

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
    time_script = get_or_create_gauge(
        'freebox_time_script', 'Metrics generation time')
    end_time = time.time()
    duration = end_time - start_time
    formatted_duration = "{:.2f}".format(duration)
    time_script.set(formatted_duration)


def optimize_code(headers):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(system_metrics, headers),
            executor.submit(lan_browser_pub_metrics, headers),
            executor.submit(lan_config, headers),
            executor.submit(port_forwarding, headers),
            executor.submit(port_incoming, headers),
            executor.submit(vpn_connection, headers),
            executor.submit(rrd_net, headers),
            executor.submit(rrd_switch, headers),
            executor.submit(storage_disk, headers)
        ]
        concurrent.futures.wait(futures)


def system_metrics(headers):
    system_request = get_request("system/", headers=headers)
    temp_t1 = system_request['result']['sensors'][1]['value']
    temp_t2 = system_request['result']['sensors'][0]['value']
    temp_t3 = system_request['result']['sensors'][2]['value']
    temp_cpu_cp_master = system_request['result']['sensors'][3]['value']
    temp_cpu_ap = system_request['result']['sensors'][4]['value']
    temp_cpu_cp_slave = system_request['result']['sensors'][5]['value']
    temp = get_or_create_gauge('freebox_temperature', 'Température', labelnames=[
                               'temp_t1', 'temp_t2', 'temp_t3', 'temp_cpu_cp_master', 'temp_cpu_ap', 'temp_cpu_cp_slave'])
    temp.labels(temp_t1=temp_t1, temp_t2=temp_t2, temp_t3=temp_t3, temp_cpu_cp_master=temp_cpu_cp_master,
                temp_cpu_ap=temp_cpu_ap, temp_cpu_cp_slave=temp_cpu_cp_slave)

    fan0_speed = system_request['result']['fans'][1]['value']
    fan1_speed = system_request['result']['fans'][0]['value']
    fans = get_or_create_gauge('freebox_fan_speed', 'Ventilateur', labelnames=[
                               'fan0_speed', 'fan1_speed'])
    fans.labels(fan0_speed=fan0_speed, fan1_speed=fan1_speed)

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
        active = item['active']
        vendor_name = item['vendor_name']
        host_type = item['host_type']
        last_time_reachable = item['last_time_reachable']
        ip = item['l3connectivities'][0]['addr']
        reachable = item.get('reachable', False)
        last_activity = item['last_activity']
        default_name = item['default_name']
        connectivity_type = item.get(
            'access_point', {}).get('connectivity_type', '')
        first_activity = item['first_activity']
        primary_name = item['primary_name']
        lan_browser_pub = get_or_create_gauge('freebox_lan_browser_pub', 'Lan browser pub', [
                                              'mac_address', 'active', 'vendor_name', 'host_type', 'last_time_reachable', 'ip', 'last_activity', 'connectivity_type', 'default_name', 'first_activity', 'primary_name'])
        lan_browser_pub.labels(mac_address=mac_address, active=active, vendor_name=vendor_name, host_type=host_type, last_time_reachable=last_time_reachable, ip=ip,
                               last_activity=last_activity, connectivity_type=connectivity_type, default_name=default_name, first_activity=first_activity, primary_name=primary_name).set(1 if reachable else 0)


def lan_config(headers):
    lan_config_request = get_request("lan/config/", headers=headers)
    name_dns = lan_config_request['result']['name_dns']
    name_mdns = lan_config_request['result']['name_mdns']
    name = lan_config_request['result']['name']
    mode = lan_config_request['result']['mode']
    name_netbios = lan_config_request['result']['name_netbios']
    ip = lan_config_request['result']['ip']
    lan_config = get_or_create_gauge('freebox_lan_config', 'Lan config', [
                                     'name_dns', 'name_mdns', 'name', 'mode', 'name_netbios', 'ip'])
    lan_config.labels(name_dns=name_dns, name_mdns=name_mdns,
                      name=name, mode=mode, name_netbios=name_netbios, ip=ip)


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
            port_forwarding = get_or_create_gauge('freebox_port_forwarding', 'Port forwarding', [
                                                  'id', 'enabled', 'ip_proto', 'wan_port_start', 'wan_port_end', 'lan_ip', 'lan_port', 'hostname', 'host', 'src_ip', 'comment'])
            port_forwarding.labels(id=id, enabled=enabled, ip_proto=ip_proto, wan_port_start=wan_port_start, wan_port_end=wan_port_end,
                                   lan_ip=lan_ip, lan_port=lan_port, hostname=hostname, host=host, src_ip=src_ip, comment=comment).set(1 if enabled else 0)


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
        port_incoming = get_or_create_gauge('freebox_port_incoming', 'Port incoming', [
                                            'id', 'enabled', 'type', 'active', 'max_port', 'min_port', 'in_port', 'readonly', 'netns'])
        port_incoming.labels(id=id, type=type, enabled=enabled, active=active, max_port=max_port,
                             min_port=min_port, in_port=in_port, readonly=readonly, netns=netns).set(1 if enabled else 0)


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
        vpn_connection = get_or_create_gauge('freebox_vpn_connection', 'User connect to VPN', [
                                             'rx_bytes', 'tx_bytes', 'user', 'vpn', 'src_port', 'src_ip', 'auth_time', 'local_ip'])
        vpn_connection.labels(rx_bytes=rx_bytes, tx_bytes=tx_bytes, user=user, vpn=vpn,
                              src_port=src_port, src_ip=src_ip, auth_time=auth_time, local_ip=local_ip)


def rrd_net(headers):
    session_data = {
        "db": "net",
        "fields": ["bw_up", "bw_down", "rate_up", "rate_down", "vpn_rate_up", "vpn_rate_down"],
        "precision": 10
    }
    rrd_net_request = post_with_headers_request(
        "rrd/", session_data, headers=headers)
    data0_request = rrd_net_request['result']['data'][0]
    bw_up = data0_request.get('bw_up', '')
    bw_down = data0_request.get('bw_down', '')
    rate_up = data0_request.get('rate_up', '')
    rate_down = data0_request.get('rate_down', '')
    vpn_rate_up = data0_request.get('vpn_rate_up', '')
    vpn_rate_down = data0_request.get('vpn_rate_down', '')
    rrd_net = get_or_create_gauge('freebox_net_states', 'Net stats', [
                                  'bw_up', 'bw_down', 'rate_up', 'rate_down', 'vpn_rate_up', 'vpn_rate_down'])
    rrd_net.labels(bw_up=bw_up, bw_down=bw_down, rate_up=rate_up,
                   rate_down=rate_down, vpn_rate_up=vpn_rate_up, vpn_rate_down=vpn_rate_down)


def rrd_switch(headers):
    session_data = {
        "db": "switch",
        "fields": ["rx_1", "tx_1", "rx_2", "tx_2", "rx_3", "tx_3", "rx_4", "tx_4"],
        "precision": 10
    }
    rrd_switch_request = post_with_headers_request(
        "rrd/", session_data, headers=headers)
    data0_request = rrd_switch_request['result']['data'][0]
    rx_1 = data0_request.get('rx_1', '')
    tx_1 = data0_request.get('tx_1', '')
    rx_2 = data0_request.get('rx_2', '')
    tx_2 = data0_request.get('tx_2', '')
    rx_3 = data0_request.get('rx_3', '')
    tx_3 = data0_request.get('tx_3', '')
    rx_4 = data0_request.get('rx_4', '')
    tx_4 = data0_request.get('tx_4', '')
    rrd_switch = get_or_create_gauge('freebox_switch_states', 'Switch stats', [
                                     'rx_1', 'tx_1', 'rx_2', 'tx_2', 'rx_3', 'tx_3', 'rx_4', 'tx_4'])
    rrd_switch.labels(rx_1=rx_1, tx_1=tx_1, rx_2=rx_2, tx_2=tx_2,
                      rx_3=rx_3, tx_3=tx_3, rx_4=rx_4, tx_4=tx_4)


def storage_disk(headers):
    storage_disk_request = get_request("storage/disk/", headers=headers)
    if 'result' in storage_disk_request and storage_disk_request['success']:
        for item in storage_disk_request['result']:
            idle_duration = item['idle_duration']
            read_error_requests = item['read_error_requests']
            read_requests = item['read_requests']
            spinning = item['spinning']
            table_type = item['table_type']
            firmware = item['firmware']
            type = item['type']
            idle = item['idle']
            connector = item['connector']
            id = item['id']
            write_error_requests = item['write_error_requests']
            state = item['state']
            write_requests = item['write_requests']
            total_bytes = item['total_bytes']
            model = item['model']
            active_duration = item['active_duration']
            temp = item['temp']
            serial = item['serial']
            fstype = item['partitions'][0]['fstype']
            label = item['partitions'][0]['label']
            internal = item['partitions'][0]['internal']
            fsck_result = item['partitions'][0]['fsck_result']
            free_bytes = item['partitions'][0]['free_bytes']
            used_bytes = item['partitions'][0]['used_bytes']
            path = item['partitions'][0]['path']
        storage_disk = get_or_create_gauge('freebox_storage_disk', 'Disk status', ['idle_duration', 'read_error_requests', 'read_requests', 'spinning', 'table_type', 'firmware', 'type', 'idle', 'connector',
                                           'id', 'write_error_requests', 'state', 'write_requests', 'total_bytes', 'model', 'active_duration', 'temp', 'serial', 'fstype', 'label', 'internal', 'fsck_result', 'free_bytes', 'used_bytes', 'path'])
        storage_disk.labels(idle_duration=idle_duration, read_error_requests=read_error_requests, read_requests=read_requests, spinning=spinning, table_type=table_type, firmware=firmware, type=type, idle=idle, connector=connector, id=id, write_error_requests=write_error_requests,
                            state=state, write_requests=write_requests, total_bytes=total_bytes, model=model, active_duration=active_duration, temp=temp, serial=serial, fstype=fstype, label=label, internal=internal, fsck_result=fsck_result, free_bytes=free_bytes, used_bytes=used_bytes, path=path)
