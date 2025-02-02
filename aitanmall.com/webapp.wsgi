#!/usr/bin/python
import sys
import logging

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/aitanmall.com/")

from webApp import app as application

if __name__ == "__main__":
    application.run(debug = True)