import time
import os
from dotenv import load_dotenv
from api_session import open_session, close_session
from api_expose import start_prometheus, system_metrics, lan_browser_pub_metrics, lan_config, port_forwarding, port_incoming, time_script, vpn_connection, rrd_net

load_dotenv()
interrupted = False
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
        time_script(start_time)
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
