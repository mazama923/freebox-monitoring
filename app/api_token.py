import json
import time
from dotenv import load_dotenv
from api_request import get_request, post_request
import os


def save_token(token):
    load_dotenv()
    with open(os.getenv("TOKEN_FILE_PATH"), "w") as token_file:
        json.dump(token, token_file)
    time.sleep(10)


def load_token():
    try:
        load_dotenv()
        with open(os.getenv("TOKEN_FILE_PATH"), "r") as token_file:
            return json.load(token_file)
    except FileNotFoundError:
        return None


def obtain_app_token():
    load_dotenv()
    data = {
        "app_id": os.getenv("APP_ID"),
        "app_name": os.getenv("APP_NAME"),
        "app_version": os.getenv("APP_VERSION"),
        "device_name": os.getenv("DEVICE_NAME"),
    }

    response = post_request("login/authorize", data)

    if response["success"]:
        track_id = response["result"]["track_id"]
        print("Veuillez autoriser l'application.")

        start_time = time.time()
        while time.time() - start_time < 600:  # 10 min
            authorization_status = get_request(f"login/authorize/{track_id}")
            status = authorization_status["result"]["status"]

            if status == "granted":
                app_token = response["result"]["app_token"]
                save_token({"app_token": app_token})
                print("Autorisation accordée. Token enregistré.")
                break
            elif status == "denied":
                print("Autorisation refusée.")
                break
            elif status == "timeout" or status == "unknown":
                print("Temps d'attente écoulé ou statut inconnu.")
                break

            time.sleep(15)
