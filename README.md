# flup

## Installation Instructions

1. `sudo apt-get install python3-venv python3-dev python3-setuptools python3-mysqldb python3-pip libapache2-mod-wsgi-py3 git build-essential`
2. `git clone https://github.com/daserzw/flup.git /opt/flup`
3. `python3 -m pip install virtualenv`
4. `cd /opt/flup ; virtualenv /opt/flup/venv`
5. `sudo chown www-data:www-data /opt/flup/flup/data`
6. `source venv/bin/activate`
7. `pip install --upgrade pip`
8. `pip install -r requirements.txt`
9. `export FLASK_APP=flup`
10. `flask run` to run the development server
