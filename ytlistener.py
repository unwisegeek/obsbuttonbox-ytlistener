import pytchat
import youtubechat
import requests
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import sys
from time import sleep
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
        print("Subscribed to Twitch Chat")

def mqtt_on_message(mqttc, userdata, msg):
    payload = eval(msg.payload.decode('utf-8'))
    if payload['author'] != "None":
        msg = f"[Twitch] {payload['author']}: {payload['msg']}"
    else:
        msg = f"{payload['msg']}"
    print(f"Sending: {msg}")
    chatOut.send_message(msg, livechat_id)
    
def mqtt_publish(author, msg):
    publish.single(
            'ytchat', 
            str(dict(author=author, msg=msg, service="Youtube")),
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
    chatOut = youtubechat.YoutubeLiveChat("oauth_creds", [livechat_id])
    chatOut.start()
    print("Started chatOut")
except youtubechat.ytchat.YoutubeLiveChatError:
    print("You blew the budget. Listening only.")
    mqtt_publish("None", "YouTube listener in listen mode only. No messages will be shared from Twitch to YouTube.")


mqttc = mqtt.Client()
mqttc.on_connect = mqtt_on_connect
mqttc.on_message = mqtt_on_message
if MQTT_AUTH == None:
    mqttc.username_pw_set(
        username=None, 
        password=None,
        )
else:
    mqttc.username_pw_set(
        username=MQTT_AUTH["username"],
        password=MQTT_AUTH["password"]
        )
mqttc.connect(MQTT_HOST, MQTT_PORT, 15)
mqttc.loop_start()

try:
    vid = sys.argv[1]
except IndexError:
    vid = input("Please enter the video ID: ")

try:
    chatIn = pytchat.create(video_id=vid)
except pytchat.exceptions.InvalidVideoIdException:
    print(f"Invalid Video ID: {vid}.")
    sys.exit()
if chatIn.is_alive():
    mqtt_publish("None", "YouTube chat is connected to Twitch chat.")
    pass
else:
    mqtt_publish("None", "YouTube chat could not connect to Twitch chat. Stream not alive.")
    pass
while chatIn.is_alive():
    for c in chatIn.get().sync_items():
        sleep(5)
        mqtt_publish(c.author.name, c.message)
        r = requests.get(f"http://{API_URL}:{API_PORT}/api/newchatmsg?author={c.author.name}&color=ffc0c0&msg={c.message}&service=YouTube")

