import hmac
import hashlib
from api_request import get_request
from api_token import load_token, obtain_app_token


def obtain_password():
    stored_token = load_token()
    if stored_token:
        app_token = stored_token["app_token"]
    else:
        obtain_app_token()
    challenge_response = get_request("login")
    challenge = challenge_response["result"]["challenge"]
    password = hmac.new(app_token.encode(),
                        challenge.encode(), hashlib.sha1).hexdigest()
    return password
