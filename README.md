# gve_devnet_meraki_fire_alarm_detection
The purpose of this sample code is to notify about an occurring fire alarm based on the audio detection feature of Meraki MV cameras. 
In case of a fire alarm, a Webex message is sent to a predefined room for each camera detecting the alarm. 
Further information about the confidence value of a detected event and data about the associated camera provide additional insights. 
The script supports up to two cameras.

## Contacts
* Ramona Renner

## Solution Components
* One or two Meraki MV cameras
* Meraki Dashboard access
* Local or online MQTT broker e.g. Mosquitto 

## Workflow

![/IMAGES/workflow.png](/IMAGES/workflow.png)

## High Level Architecture

![/IMAGES/high_level.png](/IMAGES/high_level.png)

## Prerequisites
#### MQTT Broker

MQTT is a Client-Server publish/subscribe messaging transport protocol. This sample code requires the setup of a locally installed or use of an online MQTT broker that gathers the data from all cameras and publish it to our sample script. 
Popular MQTT brokers are, for example: Mosquitto or HiveMQ.

Online brokers are easier to set up and use, but can involve delays in data delivery. For simplicity, example values for the use of an online broker are mentioned in the next sections.

In case the use of a local broker is preferred, the [Meraki Mosquitto - MQTT Broker Guide](https://developer.cisco.com/meraki/mv-sense/#!mqtt/mosquitto--mqtt-broker) describes the configuration of a local broker.

#### Meraki MQTT Setup

In the Meraki Dashboard:

1. Start by navigating to **Cameras > Monitor > Cameras** and selecting the camera you would like to enable MV Sense on.
2. Once the camera is selected, go to **Settings > Sense**.
3. Enable the **Sense API** and **Audio Detection**.
4. To enable MQTT on your camera and create a new MQTT broker configuration, click **Add or edit MQTT Brokers**.

Enter the following information for your broker:

1. **Broker Name** – Name for the broker. e.g. Mosquitto Broker
2. **Host** – This could be an IP address or hostname. e.g. test.mosquitto.org
3. **Port** – TCP port number for MQTT. e.g. 1883
4. **Security** – Enable or disable TLS. 
> Note: For demo purposes, use **None** as value for the field **Security**. Please be aware that it is recommended to use TLS in production setups. Further adaptions of this code are required for the latter. 
5. Optionally, test the connection between the camera and the broker to ensure communication.

Furter information is available in the official [Meraki MV MQTT Guide](https://developer.cisco.com/meraki/mv-sense/#!mqtt/configuring-mqtt-in-the-dashboard).

![/IMAGES/MQTT_dashboard.png](/IMAGES/MQTT_dashboard.png)


## Prepare the Webex Space

The notification is sent to a defined Webex Space. Therefore, it is recommended to create a dedicated space. 

Follow the [Instructions to Create a New Space](https://collaborationhelp.cisco.com/en-us/article/hk71r4/Webex-App-%7C-Create-a-space). In the process choose a name for the space (e.g. Meraki Fire Alarm Notifier) and add all people to notify to the space. 
 

## Installation/Configuration

1. Make sure Python 3 and Git is installed in your environment, and if not, you may download Python 3 [here](https://www.python.org/downloads/) and Git as described [here](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).
2. Create and activate a virtual environment for the project ([Instructions](https://docs.python.org/3/tutorial/venv.html)).
3. Access the created virtual environment folder
    ```
    cd [add name of virtual environment here] 
    ```
4. Clone this Github repository:  
  ```git clone [add github link here]```
  * For Github link: 
      In Github, click on the **Clone or download** button in the upper part of the page > click the **copy icon**  
      ![/IMAGES/giturl.png](/IMAGES/giturl.png)
  * Or simply download the repository as zip file using 'Download ZIP' button and extract it
4. Access the downloaded folder:  
    ```cd gve_devnet_meraki_firealarm_detection```

5. Install all dependencies:  
  ```pip3 install -r requirements.txt```


6. Configure the environment variables in **.env** file:  
      
  ```python 
    MQTT_BROKER_URL="[URL or IP of local or online MQTT broker, e.g. test.mosquitto.org]" 
    MQTT_BROKER_PORT="[MQTT port, e.g. 1883]"
    
    MERAKI_API_TOKEN="[Meraki API Token - instructions available below.]"
    MERAKI_ORGA_ID="[Id of the Meraki organization one or both cameras are associated to. Instruction below.]"

    WEBEX_TEAMS_ACCESS_TOKEN="[Webex Personal access token - instructions below.]"
    ROOM_ID="[Id of Webex space to send the fire alarm notification to.]"
  ```

> Note: Follow the instructions [here](https://developer.cisco.com/meraki/api/#!authorization/obtaining-your-meraki-api-key) to obtain the Meraki API Token.

> Note: Retrieve the organization ID via the interactive API documentation and the [Get Organizations Call](https://developer.cisco.com/meraki/api-v1/#!get-organizations).

> Note: For simplicity, follow the instructions [here](https://developer.webex.com/docs/getting-started) to obtain the Webex Personal access token. Webex Personal access tokens are for testing purposes and thereby expire 12 hours after you sign in to the Developer Portal. Simply renewed the token after that time. Other authentication methods are available for production environments. 

> Note: Retrieve the room ID of the created space via the [List Rooms API Call](https://developer.webex.com/docs/api/v1/rooms/list-rooms) and interactive API documentation.


## Starting the Application

Run the script by using the command:
```
python3 app.py
```

## Configuring the Settings

Assuming you kept the default parameters for starting the Flask application, the address to navigate would be: http://localhost:5000

![/IMAGES/settings.png](/IMAGES/settings.png)

Fill in all settings form fields and save the changes. 

Form field descriptions:

* **MV Camera 1/2** - Serial Number: Serial number of Meraki MV Camera

* **Confidence Threshold (x.xx%):** Percentage confidence threshold value of a fire alarm event that has to be exceeded before a notification is sent. Default: 0.90.
* **Reviewing Interval (ms):** Milliseconds interval in which received MQTT MV messages are reviewed based on the timestamp of the message. Default: Default: 300.
* **Pre-Notification Interval Counter:** Number of review intervals that indicate a fire alarm event above the confidence threshold before a notification is sent. Dafault: 5.
* **Notification Interval (ms):** Time span between notifications in milliseconds. This value is furthermore used to reset the Pre-Notification Interval Counters on a regular basis. Default: 60000.


## Usage

A Webex message is sent to the defined space as soon as the camera detects fire alarm sound. The CLI output show the steps from incoming message, over the validation process to the sending of a message. 

## Screenshot

![/IMAGES/giturl.png](/IMAGES/screenshot1.png)

### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.