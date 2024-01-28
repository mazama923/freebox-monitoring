from dotenv import load_dotenv
from api_request import post_request
from api_password import obtain_password
import os
import requests
import time
from api_request import get_url


def open_session():
    load_dotenv()

    max_attempts = 3
    attempts = 0

    while attempts < max_attempts:
        password = obtain_password()

        session_data = {
            "app_id": os.getenv("APP_ID"),
            "password": password
        }
        session_response = post_request("login/session/", session_data)

        if session_response["success"]:
            session_token = session_response["result"]["session_token"]
            headers = {"X-Fbx-App-Auth": session_token}
            print("Session open: Success")
            return headers
        else:
            attempts += 1
            print("Session open: Fail")
            print(session_response)
            if attempts < max_attempts:
                time.sleep(1)


def close_session(headers):
    load_dotenv()
    url_api = get_url()
    session_response = requests.post(
        url_api + "login/logout/", headers=headers, verify=os.getenv("CERT_FILE_PATH"))
    return session_response.json()
