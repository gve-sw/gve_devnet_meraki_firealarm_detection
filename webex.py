""" Copyright (c) 2022 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
           https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied. 
"""

from webexteamssdk import WebexTeamsAPI
from dotenv import load_dotenv
import os

import meraki_api
import helpers

load_dotenv()

NOTIFY_CARD_JSON_PATH = "notifyCard.json"

def prepare_alert_card(timestamp, device_info, confidence_value):
    """Add custom data to card template"""

    adapted_card = helpers.read_json(NOTIFY_CARD_JSON_PATH)

    #Meraki device Info
    name = device_info[0]['name'] 
    serial = device_info[0]['serial'] 
    lng = str(device_info[0]['lng']) 
    lat = str(device_info[0]['lat']) 
    notes = device_info[0]['notes']

    #Format timestamp to human readable
    readable_timestamp = helpers.epoch_to_iso_time(timestamp)
    
    adapted_card['body'][1]['columns'][1]['items'][0]['text'] = readable_timestamp #incident_time
    adapted_card['body'][1]['columns'][1]['items'][1]['text'] = str(confidence_value*100) + '%'   #confidence name
    adapted_card['body'][1]['columns'][1]['items'][4]['text'] = name  #camera name
    adapted_card['body'][1]['columns'][1]['items'][5]['text'] = serial #camera serial
    adapted_card['body'][1]['columns'][1]['items'][6]['text'] = lat #latitude
    adapted_card['body'][1]['columns'][1]['items'][7]['text'] = lng #longitude
    adapted_card['body'][1]['columns'][1]['items'][8]['text'] = notes #notes
    
    return adapted_card


def send_notification(timestamp, serial, confidence_value):
    """Send notification to defined Webex room. """

    WEBEX_API = WebexTeamsAPI(access_token=os.environ['WEBEX_TEAMS_ACCESS_TOKEN'])
    ROOM_ID= os.environ['ROOM_ID']
    MERAKI_ORGA_ID = os.environ['MERAKI_ORGA_ID']

    device_info = meraki_api.get_organization_device_by_serial(MERAKI_ORGA_ID, serial)

    card_content = prepare_alert_card(timestamp, device_info, confidence_value)

    attachment={
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": card_content    
        }

    WEBEX_API.messages.create(roomId=ROOM_ID, text="If you see this your client cannot render cards.", attachments=[attachment])

