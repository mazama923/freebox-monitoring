import requests
from dotenv import load_dotenv
import os


def get_url():
    load_dotenv()
    freebox_api_version_request = requests.get(
        os.getenv("BASE_API_URL") + "/api_version", params=None, headers=None, verify=os.getenv("CERT_FILE_PATH")).json()
    freebox_api_version = freebox_api_version_request["api_version"]
    freebox_major_api_version = freebox_api_version.split('.')[0]
    api_url = os.getenv("BASE_API_URL") + "/api/v" + \
        freebox_major_api_version + "/"
    return api_url


def get_request(endpoint, params=None, headers=None):
    url_api = get_url()
    response = requests.get(url_api + endpoint, params=params,
                            headers=headers, verify=os.getenv("CERT_FILE_PATH"))
    return response.json()


def post_request(endpoint, data):
    url_api = get_url()
    response = requests.post(
        url_api + endpoint, json=data, verify=os.getenv("CERT_FILE_PATH"))
    return response.json()


def post_with_headers_request(endpoint, data, headers=None):
    url_api = get_url()
    response = requests.post(url_api + endpoint, json=data,
                             headers=headers, verify=os.getenv("CERT_FILE_PATH"))
    return response.json()
