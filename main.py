import time
import os
from dotenv import load_dotenv
from prometheus_client import start_http_server, Gauge, Info
from api_request import get_request
from api_session import open_session, close_session

load_dotenv()
interrupted = False

temp_t1 = Gauge('freebox_temperature_t1', 'Température 1')
temp_t2 = Gauge('freebox_temperature_t2', 'Température 2')
temp_t3 = Gauge('freebox_temperature_t3', 'Température 3')
temp_cpu_cp_master = Gauge('freebox_temperature_cpu_cp_master', 'Température CPU CP Master')
temp_cpu_ap = Gauge('freebox_temperature_cpu_ap', 'Température CPU AP')
temp_cpu_cp_slave = Gauge('freebox_temperature_cpu_cp_slave', 'Température CPU CP Slave')
fan0_speed = Gauge('freebox_fan_speed_0', 'Ventilateur 1')
fan1_speed = Gauge('freebox_fan_speed_1', 'Ventilateur 2')
firmware_version = Info('freebox_firmware_version', 'Firmware version')
start_from = Gauge('freebox_start_from', 'uptime_val')

lan_browser_pub_gauge = Gauge('freebox_lan_browser_pub', 'LAN Browser Pub Metric')

start_http_server(8000)

try:
    while True:
        headers = open_session()

        system_request = get_request("system/", headers=headers)

        temp_t2.set(system_request['result']['sensors'][0]['value'])
        temp_t1.set(system_request['result']['sensors'][1]['value'])
        temp_t3.set(system_request['result']['sensors'][2]['value'])
        temp_cpu_cp_master.set(system_request['result']['sensors'][3]['value'])
        temp_cpu_ap.set(system_request['result']['sensors'][4]['value'])
        temp_cpu_cp_slave.set(system_request['result']['sensors'][5]['value'])

        fan0_speed.set(system_request['result']['fans'][1]['value'])
        fan1_speed.set(system_request['result']['fans'][0]['value'])

        firmware_version.info({'version': system_request['result']['firmware_version']})

        start_from.set(system_request['result']['uptime_val'])

        lan_browser_pub_request = get_request("lan/browser/pub/", headers=headers)
        lan_browser_pub_gauge.set(lan_browser_pub_request['your_metric_key']) 
        print(lan_browser_pub_request)
        time.sleep(int(os.getenv("SCRAPE_INTERVAL")))

except KeyboardInterrupt:
    interrupted = True
    close_response = close_session(headers)
    if "success" in close_response and close_response["success"]:
        print("Session close.")
    else:
        print("Logout failed.")
        print(close_response)
finally:
    if not interrupted:
        close_response = close_session(headers)
        if "success" in close_response and close_response["success"]:
            print("Session close.")
        else:
            print("Logout failed.")
            print(close_response)
