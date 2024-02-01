# freebox-monitoring

Monitoring tool for the freebox delta.

Using prometheus to retrieve metrics from the free api and grafana for visualization.

![Grafana1](https://github.com/mazama923/freebox-monitoring/blob/main/doc/img/grafana1.png)

![Grafana2](https://github.com/mazama923/freebox-monitoring/blob/main/doc/img/grafana2.png)

Link for dashboard: https://grafana.com/grafana/dashboards/20394-freebox-monitoring/

## Installation

#### Installation with docker ( recommended )

The docker image contains the contents of the app folder, it already exposes port 8000 so that prometheus can scrape them.
An example of docker compose is provided in the project.

Use the latest available image from the project:
https://hub.docker.com/repository/docker/benlexa/freebox-monitoring/general


```yml
  freebox-monitoring:
    image: benlexa/freebox-monitoring:latest
    container_name: freebox-monitoring
    restart: always
    volumes:
      - /path/to/token:/token
    networks:
      - monitoring
```

- In order to keep the token given by your freebox when it restarts, you will need to specify the path to the folder to store your token.
- if you already have a prometheus and grafana available from you, adapt the network to your needs

#### Installation manual

**Prérequis:** Have python and pip installed on your host machine

```bash
git clone git@github.com:mazama923/freebox-monitoring.git
```
```bash
cd freebox-monitoring/app/
```
```bash
pip install -r requirements.txt
```
```bash
vi .env
```

Adapt the paths to your needs

```env
APP_ID = "freebox.monitoring"
APP_NAME = "FreeboxMonitoring"
APP_VERSION = "0.0.1"
DEVICE_NAME = "FreeboxMonitoring"

BASE_API_URL = "https://mafreebox.freebox.fr"

TOKEN_FILE_PATH = /token/token.json
CERT_FILE_PATH = /app/cert/freebox_ecc_root_ca.pem
SCRAPE_INTERVAL = 30
PORT_HTTP = 8000
```
```bash
python3 main.py
```



## Usage

Once the application starts you have 10 minutes to validate the authentication on the screen of your freebox.

once validated, go to your freebox panel.
- Paramètres de la Freebox > Gestion des accès > Applications

And add the right: **Modification des réglages de la Freebox**

![Rights](https://github.com/mazama923/freebox-monitoring/blob/main/doc/img/rights.png)

once done the application is ready and able to retrieve the metrics
