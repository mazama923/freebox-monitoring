import os
from dotenv import load_dotenv
from prometheus_client import start_http_server, Gauge

def start_prometheus():
    start_http_server(8000)
