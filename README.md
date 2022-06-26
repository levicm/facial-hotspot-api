# facial-hotspot-api
## Install
To install the project, open a shell session and execute the commands:

Obs.: tested on Ubuntu 20+.
### Ubuntu 20+
```shell
git clone https://github.com/levicm/facial-hotspot-api.git
cd facial-hotspot-api
sudo apt update
sudo apt install python3 python3-pip python3-venv python3-dev build-essential
python3 -m venv venv
source venv/bin/activate
pip install wheel
pip install -r requirements.txt
```
## Run

```shell
uvicorn app:app --debug
```
