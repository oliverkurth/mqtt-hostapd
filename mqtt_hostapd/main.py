import paho.mqtt.client as mqtt
import socket
import os

# HTTP settings
PORT = 8000
USE_HTTPS = False

# MQTT settings
MQTT_SERVER="192.168.2.22"
MQTT_PORT=1883

TOPIC="hostapd"

HOSTAPD_CTRL = "/var/run/hostapd/ap1"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.is_connected = True


def on_disconnect(client, userdata, rc):
    client.is_connected = False
    if rc != mqtt.MQTT_ERR_SUCCESS:
        print ("unexpected MQTT disconnect\n")


def connect_hostapd():
    s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    s.settimeout(10)
    s_local = "/tmp/mqtt-hostapd-{}".format(os.getpid())
    s.bind(s_local)
    s.connect(HOSTAPD_CTRL)
    s.send("ATTACH")

    response = s.recv(1024)
    if not response.startswith("OK"):
        raise Exception("unexpected response from hostapd: {}\n".format(response))

    return s


def parse_hostapd_data(data):
    what,mac = data[data.find(">") + 1:].split(' ')
    return what, mac


def main():
    client = mqtt.Client()
    client.is_connected = False
    client.connect(MQTT_SERVER, MQTT_PORT, 60)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    s = connect_hostapd()

    while True:
        client.loop()

        try:
            data = s.recv(1024)
            what, mac = parse_hostapd_data(data)
            if what == "AP-STA-CONNECTED":
                what = "connected"
            elif what == "AP-STA-DISCONNECTED":
                what = "disconnected"
            else:
                what = "unknown"
            print ("{} {}".format(what, mac))

            if not client.is_connected:
                print ("MQTT reconnect\n")
                client.reconnect()

            client.publish("stat/{}/{}".format(TOPIC, mac), what)
        except socket.timeout:
            pass


if __name__ == "__main__":
    main()
