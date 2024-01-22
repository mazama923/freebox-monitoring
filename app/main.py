import time
import os
from dotenv import load_dotenv
from api_session import open_session, close_session
from api_expose import start_prometheus, system_metrics, lan_browser_pub_metrics, lan_config, port_forwarding, port_incoming, time_script, vpn_connection, rrd_net, rrd_switch, storage_disk

load_dotenv()
start_prometheus()
headers = open_session()

try:
    while True:
        start_time = time.time()
        system_metrics(headers)
        lan_browser_pub_metrics(headers)
        lan_config(headers)
        port_forwarding(headers)
        port_incoming(headers)
        vpn_connection(headers)
        rrd_net(headers)
        rrd_switch(headers)
        storage_disk(headers)
        time_script(start_time)
        time.sleep(int(os.getenv("SCRAPE_INTERVAL")))

finally:
    close_response = close_session(headers)
    if "success" in close_response and close_response["success"]:
        print("Session close.")
    else:
        print("Logout failed.")
        print(close_response)
