import RPi.GPIO as GPIO
import datetime
import time
import paho.mqtt.client as mqtt
from grovepi import *

debug = True

led_color = "green"
led_green = 3
led_red = 4

gpio_channel = 17
pinMode(led_green, "OUTPUT")
pinMode(led_red, "OUTPUT")

mqtt_ip = "192.168.1.100"
mqtt_port = 1883
mqtt_topic = "planten/tomaat/vochtigheid"
mqtt_debounce = 30 # seconds
mqtt_last_send = 0

def log(message):
    time_prefix = "[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "]"
    print(time_prefix + message)

def send(payload):
    client = mqtt.Client()
    client.connect(mqtt_ip, mqtt_port, 60)
    client.publish(mqtt_topic, "on");
    client.disconnect();
    mqtt_last_send = time.time()
    log("[plant] mqtt: " + payload)

def led(state):
    global led_color
    if state == "green" and led_color == "red":
        digitalWrite(led_green, 1)
        digitalWrite(led_red, 0)
        led_color = "green"
    if state == "red" and led_color == "green":
        digitalWrite(led_green, 0)
        digitalWrite(led_red, 1)
        led_color = "red"

def can_send(now):
    return now > mqtt_last_send + mqtt_debounce

def notify_need_water(now):
    if not debug and can_send(time.time()):
        send("on")

def notify_water_satisfied(now):
    if not debug and can_send(time.time()):
        send("off")

def callback(channel):
    if GPIO.input(channel):
        notify_need_water(time.time())
        led("red")
        log("[plant] need water")
    else:
        notify_water_satisfied(time.time())
        led("green")
        log("[plant] water satisfied")

GPIO.setmode(GPIO.BCM)
GPIO.setup(gpio_channel, GPIO.IN)
GPIO.add_event_detect(gpio_channel, GPIO.BOTH, bouncetime = 300)
GPIO.add_event_callback(gpio_channel, callback)

while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        sys.exit()

