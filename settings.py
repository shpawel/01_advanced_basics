#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import re

DEFAULT_CONFIG_FILE = 'config.json'

LOG_RECORD_RE_PATTERN = re.compile(
    '^'                                       # начало строки
    '(?P<remote_addr>\S+) '                   # $remote_addr
    '(?P<remote_user>\S+\s+)'                 # $remote_user
    '(?P<http_x_real_ip>\S+) '                # $http_x_real_ip    
    '(?P<time_local>\[\S+ \S+\]) '            # [$time_local]
    '(\"\S+ (?P<url>\S+) \S+\") '             # "$request"
    '(?P<status>\d+) '                        # $status
    '(?P<body_bytes_sent>\d+) '               # $body_bytes_sent
    '(?P<http_referer>\"\S+\") '              # "$http_referer"
    '(?P<user_agent>\".*\") '                 # "$http_user_agent"
    '(?P<http_x_forwarded_for>\"\S+\") '      # "$http_x_forwarded_for"
    '(?P<http_X_REQUEST_ID>\"\S+\") '         # "$http_X_REQUEST_ID"
    '(?P<http_X_RD_USER>\"\S+\") '            # "$http_X_RB_USER"
    '(?P<request_time>\d+\.\d+)'              # $request_time
    '$'                                       # конец строки
)

LOG_FILE_RE_PATTERN = re.compile(
    '^nginx-access-ui\.log-(?P<log_date>\d{8})\.(?P<log_format>(gz|txt))$'
)
