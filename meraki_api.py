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

import meraki
import os
from dotenv import load_dotenv

load_dotenv()

def get_organization_device_by_serial(orga, serial):

    DASHBOARD = meraki.DashboardAPI(
        api_key=os.environ['MERAKI_API_TOKEN'],
        base_url='https://api.meraki.com/api/v1/',
        output_log=False,
        print_console=False
        )

    response = DASHBOARD.organizations.getOrganizationDevices(orga, serial=serial)
    return response
