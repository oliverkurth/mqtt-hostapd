import json
import os
import paho.mqtt.client as mqtt
import socket
import yaml

CONFIG_FILE = "config.yaml"

# MQTT settings
MQTT_SERVER="192.168.2.22"
MQTT_PORT=1883
MQTT_STATE_TOPIC = "state/hostapd"
MQTT_ID_PREFIX = "hostapd-"

HOSTAPD_CTRL_DIR = "/var/run/hostapd"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.is_connected = True


def on_disconnect(client, userdata, rc):
    client.is_connected = False
    if rc != mqtt.MQTT_ERR_SUCCESS:
        print ("unexpected MQTT disconnect\n")


def connect_mqtt(mqtt_config):
    client = mqtt.Client()
    client.is_connected = False
    client.connect(mqtt_config.get('server', MQTT_SERVER), mqtt_config.get('port', MQTT_PORT), 60)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    return client


def mqtt_autodiscovery(client, mqtt_config, devices):
    if not mqtt_config.get('autodiscovery', False):
        return

    for id, device in devices.items():
        if not device.get('autodiscovery', True):
            continue
        data = {
            "state_topic" : "{}/{}".format(mqtt_config.get('state_topic', MQTT_STATE_TOPIC), id),
            "name" : device.get('name', id),
            "unique_id" : "{}{}".format(mqtt_config.get('id_prefix', MQTT_ID_PREFIX), id),
            "payload_home" : "connected",
            "payload_not_home" : "disconnected",
            "source_type" : "router"
        }
        topic = "homeassistant/device_tracker/{}/config".format(id)

        client.publish(topic, json.dumps(data))


def connect_hostapd(hostapd_config):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    s.settimeout(10)
    s_local = "/tmp/mqtt-hostapd-{}".format(os.getpid())
    s.bind(s_local)
    s.connect(os.path.join(hostapd_config.get("ctrl_dir", HOSTAPD_CTRL_DIR), hostapd_config.get("interface")))
    s.send("ATTACH")

    response = s.recv(1024)
    if not response.startswith("OK"):
        raise Exception("unexpected response from hostapd: {}\n".format(response))

    return s


def parse_hostapd_data(data):
    try:
        what, mac = data[data.find(">") + 1:].split(' ')
        id = mac.replace(':', '')
        return what, id
    except ValueError:
        print ("could not parse '{}'".format(data))
        return None, None


def main():
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)

    client = connect_mqtt(config['mqtt'])
    mqtt_autodiscovery(client, config['mqtt'], config['devices'])

    s = connect_hostapd(config["hostapd"])

    while True:
        client.loop()

        try:
            data = s.recv(1024)
            what, id = parse_hostapd_data(data)

            if what == "AP-STA-CONNECTED":
                what = "connected"
            elif what == "AP-STA-DISCONNECTED":
                what = "disconnected"
            else:
                what = "unknown"
            print ("{} {}".format(what, id))

            if what == "connected" or what == "disconnected":
                if not client.is_connected:
                    print ("MQTT reconnect\n")
                    client.reconnect()

                client.publish("{}/{}".format(config['mqtt'].get('state_topic', MQTT_STATE_TOPIC), id), what)

        except socket.timeout:
            pass


if __name__ == "__main__":
    main()
