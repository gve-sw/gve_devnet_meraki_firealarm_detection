''' Copyright (c) 2022 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
           https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied. '''

import json
import time    
from datetime import datetime
import dateutil.parser as dp


"""Read settings from settings.json"""
def read_json(settings_path):
	with open(settings_path, 'r') as f:
		jsondata = json.loads(f.read())
		f.close()
	return jsondata


"""Write settings from settings.json"""
def write_json(settings_path, data):
    with open(settings_path, 'w') as f:
        json.dump(data, f)
        f.close()


def epoch_to_iso_time(timestamp):
    """Translates epoch time stamps to iso time format"""
    dt = datetime.utcfromtimestamp(timestamp/1000)
    iso_format = dt.isoformat() + 'Z'
    return iso_format


def iso_to_epoch_timestamp(timestamp):
    """Translates iso timestamp to an epoch timestamp"""
    parsed_timestamp = dp.parse(timestamp)
    timestamp_in_seconds = parsed_timestamp.timestamp()
    return timestamp_in_seconds


def get_current_epoch_time():
    """Returns the current time as epoch time stamp"""
    return int(time.time())
