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
### Environment variables
To run preporly the app needs a environment variable to be defined with the [SQLAlchemy URL String](https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls) like this:
```
DATABASE_URL = "dialect+driver://username:password@host:port/database"
```
This can be done by one of the options:
* creating a .env file in the app directory with the entry: ```DATABASE_URL = "sqlite:///users.db"```. This is the easiest way and common on development environments. The app is ready to run on SQLite, so, this sample should work without problems;
* defining a OS environment variable. This is common on production environments.

Here are same URL string samples for common databases:
* PostgreSQL: ```postgresql://scott:tiger@localhost:5432/mydatabase```
* SQLite: ```sqlite:////absolute/path/to/foo.db```

## Run

```shell
uvicorn app:app --debug
```
