import time
import os
from dotenv import load_dotenv
from api_session import open_session, close_session
from api_expose import start_prometheus, system_metrics, lan_browser_pub_metrics, port_incoming, lan_config, time_script

load_dotenv()
interrupted = False
start_prometheus()

try:
    while True:
        start_time = time.time()
        headers = open_session()
        system_metrics(headers)
        lan_browser_pub_metrics(headers)
        port_incoming(headers)
        lan_config(headers)
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
