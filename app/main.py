import time
import os
from dotenv import load_dotenv
from api_session import open_session, close_session
from api_expose import start_prometheus, time_script, optimize_code

load_dotenv()
start_prometheus()
headers = open_session()

try:
    while True:
        start_time = time.time()
        optimize_code(headers)
        time_script(start_time)
        time.sleep(int(os.getenv("SCRAPE_INTERVAL")))

finally:
    close_response = close_session(headers)
    if "success" in close_response and close_response["success"]:
        print("Session close.")
    else:
        print("Logout failed.")
        print(close_response)
