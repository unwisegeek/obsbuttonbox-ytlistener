import pytchat
import youtubechat
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


def mqtt_on_connect(mqttc, userdata, flags, rc):
        print(f"Connected to MQTT with result code {str(rc)}")
        mqttc.subscribe("twchat")

def mqtt_on_message(mqttc, userdata, msg):
    payload = eval(msg.payload.decode('utf-8'))
    if payload['author'] != "None":
        msg = f"[Twitch] {payload['author']}: {payload['msg']}"
    else:
        msg = f"{payload['msg']}"
    chat_obj.send_message(msg, livechat_id)
    
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
    livechat_id = youtubechat.get_live_chat_id_for_stream_now("oauth_creds")
    chat_obj = youtubechat.YouTubeLiveChat("oauth_creds", [livechat_id])
    chat_obj.start()
except youtubechat.ytchat.YoutubeLiveChatError:
    print("You blew the budget. Listening only.")
    mqtt_publish("None", "YouTube listener in listen mode only. No messages will be shared from Twitch to YouTube.")


mqttc = mqtt.Client()
mqttc.on_connect = mqtt_on_connect
mqttc.on_message = mqtt_on_message

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
    pass
else:
    mqtt_publish("None", "YouTube chat could not connect to Twitch chat. Stream not alive.")
    pass
while chat.is_alive():
    for c in chat.get().sync_items():
        mqtt_publish(c.author.name, c.message)
        r = requests.get(f"http://{API_URL}:{API_PORT}/api/newchatmsg?author={c.author.name}&color=ffc0c0&msg={c.message}&service=YouTube")

