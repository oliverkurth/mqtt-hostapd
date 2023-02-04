# mqtt-hostapd
MQTT client tracking devices connecting to hostapd

## What is this?

This tracks WifI devices connecting and disconnecting from your WiFi network running [hostapd](https://w1.fi/hostapd/),
and sends the status via MQTT messages to [Homeassistant](https://www.home-assistant.io/).

With `autodiscovery` enabled, the devices will be automatically seen in HA without any configuration required in HA.

## Requirements

Hostapd installed and running. python. An MQTT server somewhere on your network.

Probably Homeassistant running somewhere on your network, but in principle this can be used with anything that understands MQTT.

## Installation:

This needs to be installed on the same host as hostapd.

```
pip install -r requirements.txt
pip install .
```

Edit the file `config.yaml.exampple` and configure (at least) your MQTT server, and probably the interface name for `hostapd`.

Under `devices`, add devices (probably your families phones) to be tracked. The keys are the MAC addresses of the WifI devices, but with colons removed.
So `11:22:33:44:55:66` becomes `112233445566`.

You can test with just running `mqtt-hostapd`. If `autodiscovery` is enabled,
you should immediately see devices in Homeassistant under Settings/Entities, when you search for "device_tracker".
To test the status, turn WiFi on the device off and on again.

When tested, copy the file to `/etc/mqtt-hostapd/config/yaml`.

If you use `systemd`, copy `mqtt-hostapd.service` to `/etc/systemd/system`,
start with `systemctl start mqtt-hostapd`, and enable with `systemctl enable mqtt-hostapd` so it runs ater next reboot.

