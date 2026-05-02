#!/usr/bin/env python3
"""Control a Tasmota plug via MQTT."""

import argparse
import sys
import paho.mqtt.client as mqtt

MQTT_HOST = "192.168.178.213"
MQTT_PORT = 1883


def on_connect(client, userdata, flags, rc):
    if rc != 0:
        print(f"Connection failed with code {rc}", file=sys.stderr)
        sys.exit(1)


def on_message(client, userdata, msg):
    print(f"Response: {msg.payload.decode()}")
    client.disconnect()


def set_plug(plug_name: str, state: str) -> None:
    command_topic = f"cmnd/{plug_name}/POWER"
    status_topic = f"stat/{plug_name}/POWER"

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_HOST, MQTT_PORT, keepalive=10)
    client.subscribe(status_topic)
    client.publish(command_topic, state.upper())
    client.loop_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Control a Tasmota plug via MQTT")
    parser.add_argument("state", choices=["on", "off", "ON", "OFF"], help="Desired power state")
    parser.add_argument("--plug", default="plug01", help="Plug name (default: plug01)")
    args = parser.parse_args()

    set_plug(args.plug, args.state)
