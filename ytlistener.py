import pytchat
import requests
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import sys
from config import (
    MQTT_HOST,
    MQTT_PORT,
    MQTT_AUTH,
    API_URL,
    API_PORT,
)

def mqtt_publish(author, msg):
    publish.single(
            'ytchat', 
            str(dict(author=author, msg=msg)),
            qos=0, 
            retain=False, 
            hostname=MQTT_HOST,
            port=MQTT_PORT, 
            client_id="", 
            keepalive=60,
            will=None,
            auth=MQTT_AUTH,
            tls=None,
            protocol=mqtt.MQTTv311,
            transport="tcp",
            )

try:
    vid = sys.argv[1]
except IndexError:
    vid = input("Please enter the video ID: ")

try:
    chat = pytchat.create(video_id=vid)
except pytchat.exceptions.InvalidVideoIdException:
    print(f"Invalid Video ID: {vid}.")
    sys.exit()
if chat.is_alive():
    mqtt_publish("None", "YouTube chat is connected to Twitch chat.")
else:
    mqtt_publish("None", "YouTube chat could not connect to Twitch chat. Stream not alive.")
while chat.is_alive():
    for c in chat.get().sync_items():
        
        r = requests.get(f"http://{API_URL}:{API_PORT}/api/newchatmsg?author={c.author.name}&color=ffc0c0&msg={c.message}&service=YouTube")

