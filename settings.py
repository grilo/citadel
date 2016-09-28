#!/usr/bin/env python

# This is what we assume by default the messages received are encoded in
default_encoding = "utf8"
log_format = '%(asctime)s::%(levelname)s::%(message)s'
log_level = 'DEBUG'

# Pretties!
ANSI = {
    "green": '\033[33;1m',
    "red":   '\033[31;1m',
    "yellow": '\033[33;1m',
    "reset": '\033[0m'
}
