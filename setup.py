import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "requirements.txt")) as requirements_txt:
    REQUIRES = requirements_txt.read().splitlines()

setup(
    name='mqtt_hostapd',

    version='0.1',

    description='MQTT client to send connect status of devices connected to hostapd',
    long_description='MQTT client to send connect status of devices connected to hostapd',

    author='Oliver Kurth',
    author_email='okurth@gmail.com',

    license='Apache Software License',

    packages=find_packages(),
    zip_safe=False,

    install_requires=REQUIRES,

    include_package_data=True,

    entry_points={
        'console_scripts': [
            'mqtt-hostapd = mqtt_hostapd.main:main'
        ]
    },
)
