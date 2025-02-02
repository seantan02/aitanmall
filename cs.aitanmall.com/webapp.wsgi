#!/usr/bin/python
import sys
import logging

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/cs.aitanmall.com/")

from webApp import app as application
application.secret_key = "nadunawud12812nadw91228d"

if __name__ == "__main__":
    application.run(debug = True)
