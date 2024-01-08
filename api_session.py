from dotenv import load_dotenv
from api_request import post_request
from api_password import obtain_password
import os
import requests
from api_request import get_url


def open_session():
    load_dotenv()

    password = obtain_password()

    session_data = {
        "app_id": os.getenv("APP_ID"),
        "password": password
    }

    session_response = post_request("login/session/", session_data)

    if session_response["success"]:
        session_token = session_response["result"]["session_token"]
        headers = {"X-Fbx-App-Auth": session_token}
        return headers
    else:
        print("Échec de l'ouverture de session.")
    print(session_response)


def close_session(headers):
    url_api = get_url()
    session_response = requests.post(
        url_api + "login/logout/", headers=headers)
    return session_response.json()
