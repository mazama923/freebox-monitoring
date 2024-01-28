import time
import os
from dotenv import load_dotenv
from api_session import open_session, close_session
from api_expose import start_prometheus, concurrent_requests, time_script

load_dotenv()
start_prometheus()

while True:
    try:
        start_time = time.time()
        headers = open_session()
        if headers is None:
            print("Failed to open session after maximum attempts, stopping...")
            continue
        concurrent_requests(headers)
        time_script(start_time)

    finally:
        if headers is not None:
            close_response = close_session(headers)
            if "success" in close_response and close_response["success"]:
                print("Session close: Success")
                print("------")
                time.sleep(int(os.getenv("SCRAPE_INTERVAL")))
            else:
                print("Session close: Fail")
                print(close_response)
                print("------")
        elif headers is None:
            print("------")
            time.sleep(int(os.getenv("SCRAPE_INTERVAL")))
