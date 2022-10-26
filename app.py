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
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request
from flask_mqtt import Mqtt
from apscheduler.schedulers.background import BackgroundScheduler

import webex
import helpers

app = Flask(__name__)

load_dotenv()
#setup MQTT Client
app.config['MQTT_BROKER_URL'] = os.environ['MQTT_BROKER_URL']
app.config['MQTT_BROKER_PORT'] = int(os.environ['MQTT_BROKER_PORT'])
app.config['MQTT_TLS_ENABLED'] = False 
app.config['MQTT_CLEAN_SESSION'] = True
mqtt = Mqtt(app, connect_async=True)

SETTINGS_JSON_PATH="settings.json"

@app.route('/', methods=['GET', 'POST'])
def settings():
    """Route for settings page"""

    try:
        settings = helpers.read_json(SETTINGS_JSON_PATH)

        if request.method == 'GET':
            
            return render_template('settings.html', settings=settings)

        elif request.method == 'POST':

            # only uppercase MAC strings recognized as correct topic
            settings['SERIAL_MV_1'] = request.form.get("input-serial-camera1").upper() or ""
            settings['SERIAL_MV_2'] = request.form.get("input-serial-camera2").upper() or ""
            settings['REVIEWING_INTERVAL_MSECONDS'] = request.form.get("input-review-interval") or 300  
            settings['CONFIDENCE_THRESHOLD'] = float(request.form.get("input-confidence-value")) or 0.90  
            settings['NOTIFICATION_INTERVAL_COUNT'] = request.form.get("input-interval-count") or 5  
            settings['NOTIFICATION_INTERVAL_MSECONDS'] = request.form.get("input-interval-reset") or 60000  

            helpers.write_json(SETTINGS_JSON_PATH, settings)
            load_settings_from_storage()
            update_topic_subscriptions()

            return render_template('settings.html', settings=settings, success=True, successmessage="Successfully updated settings.")

    except Exception as e:
            print(e)
            return render_template('settings.html', error=True, errorcode=e)


def load_settings_from_storage():
    '''Load settings values from json file into script.'''
    global SETTINGS, MVS
    
    SETTINGS = helpers.read_json(SETTINGS_JSON_PATH)
    MVS = [SETTINGS['SERIAL_MV_1'], SETTINGS['SERIAL_MV_2']] 

'''
@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    print('MQTT Log: {}'.format(buf))
'''

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    '''Subscribe to topics for both cameras on connect.'''

    if rc==0:
        print("MQTT client connected")
    else:
        print("MQTT Bad connection. Returned code=",rc)

    update_topic_subscriptions()


@mqtt.on_message()
def on_message(client, userdata, message):
    """ Every incoming mqtt message will call this function 
    We detect messages of the format: 
    [{'confidence': 0.xxx, 'id': x, 'name': 'fireAlarm', 'ts': 'xxx'}]
    """
    mqtt_messages = json.loads(message.payload.decode("utf-8"))
    
    for mqtt_message in mqtt_messages:
        if 'name' in mqtt_message and mqtt_message['name'] == 'fireAlarm':
            serial = message.topic.split('/')[2]
            on_mv_firealarm_message(mqtt_message, serial)


def on_mv_firealarm_message(mqtt_message, serial):
    """MV firealarm message handler"""

    global MVS, mv_firealarm_cache 

    current_timestamp = int(mqtt_message['ts'])

    print("New message:" + str(mqtt_message))

    if serial in MVS:
        mv_id = MVS.index(serial)
        confidence_value = float(mqtt_message['confidence'])
        
        if message_newer_next_reviewing_timestamp(current_timestamp, mv_id):               

            if confidence_threshold_value_extended(confidence_value):
                print('Confidence value above threshold on camera: ' + str(mv_id+1))
                
                if notification_interval_passed(current_timestamp, mv_id):

                    if alarm_interval_count_passed(mv_id):
                        print('Fire alarm counter threshold passed on camera: ' + str(mv_id+1))
                        
                        trigger_notification(current_timestamp, serial, confidence_value)
                        update_alarm_cache(current_timestamp, mv_id, last_notification_timestamp=current_timestamp)
                        
                        print(f'********* Fire alarm notification sent on camera: ' + str(mv_id+1))

                    else:
                        print('Detection counter increasing to:')
                        update_alarm_cache(current_timestamp, mv_id, counter_increase=1)
                        
                else:
                    reset_cache_counter(mv_id)
                    print('Notification interval did not yet pass. Skip message and reset counter on camera: ' + str(mv_id+1))


# Scenarios function
def trigger_notification(timestamp, serial, confidence_value):
    """Method to start notification"""
    webex.send_notification(timestamp, serial, confidence_value)
        

#Helpers
def alarm_interval_count_passed(mv_id):
    """Method to check if the Pre-Notification Interval Counter Value was exceeded."""
    
    global settings

    cache_status_counter = int(mv_firealarm_cache[mv_id]['status_counter'])
    counter_settings = int(SETTINGS['NOTIFICATION_INTERVAL_COUNT'])

    return cache_status_counter >= counter_settings


def confidence_threshold_value_extended(confidence_value):  
    """Method to check if the confidence threshold was exceeded."""
    global settings

    CONFIDENCE_THRESHOLD = float(SETTINGS['CONFIDENCE_THRESHOLD'])

    return confidence_value >= CONFIDENCE_THRESHOLD


def message_newer_next_reviewing_timestamp(current_timestamp, mv_id):
    """Method to check if the reviewing interval passed and thereby a new message will get further proceeded."""

    REVIEWING_INTERVAL_MSECONDS = int(SETTINGS['REVIEWING_INTERVAL_MSECONDS'])
    global mv_firealarm_cache
    
    last_review_timestamp = int(mv_firealarm_cache[mv_id]['last_review_timestamp'])

    next_review_timestamp = last_review_timestamp + REVIEWING_INTERVAL_MSECONDS

    return current_timestamp > next_review_timestamp


def notification_interval_passed(current_timestamp, mv_id):
    """Method to check if the notification intervall passed and thereby a new message can be sent."""

    NOTIFICATION_INTERVAL_MSECONDS = int(SETTINGS['NOTIFICATION_INTERVAL_MSECONDS'])

    global mv_firealarm_cache
    
    last_notification_timestamp = int(mv_firealarm_cache[mv_id]['last_notification_timestamp'])

    next_notification_timestamp = last_notification_timestamp + NOTIFICATION_INTERVAL_MSECONDS

    return current_timestamp >= next_notification_timestamp


def update_alarm_cache(current_timestamp,  mv_id, counter_increase=0, last_notification_timestamp=None):
    """Updated the reviewing cache"""

    global mv_firealarm_cache
    mv_firealarm_cache[mv_id]['last_review_timestamp'] = current_timestamp
    mv_firealarm_cache[mv_id]['status_counter'] = mv_firealarm_cache[mv_id]['status_counter'] + counter_increase
    if last_notification_timestamp != None:
        mv_firealarm_cache[mv_id]['last_notification_timestamp'] = last_notification_timestamp

    print(mv_firealarm_cache[mv_id]['status_counter'])


def reset_cache_counter(mv_id):
    """Reset the reviewing cache"""

    global mv_firealarm_cache

    mv_firealarm_cache[mv_id]['status_counter'] = 0 

    
def generate_topic_strings():
    """Generates the topic strings bases on settings."""
    
    # only uppercase strings recognized as correct topic
    SERIAL_MV_1 = SETTINGS['SERIAL_MV_1']
    SERIAL_MV_2 = SETTINGS['SERIAL_MV_2']

    MQTT_TOPIC_MV_1 = generate_MV_audio_topic_string(SERIAL_MV_1)
    MQTT_TOPIC_MV_2 = generate_MV_audio_topic_string(SERIAL_MV_2)

    return MQTT_TOPIC_MV_1, MQTT_TOPIC_MV_2


def generate_MV_audio_topic_string(SERIAL_MV):
    return f'/merakimv/{SERIAL_MV}/audio_detections'


def update_topic_subscriptions():
    """Replace topic subscriptions for cameras"""
    mqtt.unsubscribe_all()

    MQTT_TOPIC_MV_1, MQTT_TOPIC_MV_2 = generate_topic_strings()

    mqtt.subscribe(MQTT_TOPIC_MV_1)
    mqtt.subscribe(MQTT_TOPIC_MV_2)

    print('Updated MQTT topics subscriptions to topics: ')
    print(MQTT_TOPIC_MV_1)
    print(MQTT_TOPIC_MV_2)


def alarm_stopped(mv_id):
    """Method to check if the alarm stopped. The mentioned is expected in case the last review time stamp for a camera is more than 1.5 * the notification interval in the past."""

    NOTIFICATION_INTERVAL_MSECONDS = int(SETTINGS['NOTIFICATION_INTERVAL_MSECONDS'])
    
    current_epoch_time = helpers.get_current_epoch_time()*1000

    time_of_last_notification_and_buffer = int(mv_firealarm_cache[mv_id]['last_review_timestamp']) + int(NOTIFICATION_INTERVAL_MSECONDS * 1.5)

    return current_epoch_time > time_of_last_notification_and_buffer



def reset_status_counter_after_no_alarm_period():
    """Periodic counter reset:
    We do not receive messages if the alarm stops. Thereby we manually reset the counter every once in a while in case the alarm stopped."""

    for mv_id, cameras in enumerate(MVS):
        if alarm_stopped(mv_id):
            reset_cache_counter(mv_id)
            print('Resetting counter since no alarm for a while on camera: ' + str(mv_id + 1))


def scheduler():
    '''
    Executes automatic periodic counter reset if alarm stopped.
    '''

    NOTIFICATION_INTERVAL_SECONDS = int(SETTINGS['NOTIFICATION_INTERVAL_MSECONDS'])/1000
    interval = NOTIFICATION_INTERVAL_SECONDS * 1.5

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=reset_status_counter_after_no_alarm_period, trigger="interval", seconds=interval , max_instances=1)
    scheduler.start()
    print("Scheduler Started with interval of seconds: " + str(interval))


#Main Function
if __name__ == "__main__":

    SETTINGS = {}
    MVS = [] # array of cameras 


    mv_firealarm_cache = [{'last_review_timestamp': 0, 'status_counter': 0, 'last_notification_timestamp':0},
                      {'last_review_timestamp': 0, 'status_counter': 0, 'last_notification_timestamp':0}]

    load_settings_from_storage()

    scheduler()

    app.run(host='0.0.0.0',use_reloader=False, debug=False)
    # important: Do not use reloader because this will create two Flask instances.
    # Flask-MQTT only supports running with one instance





    