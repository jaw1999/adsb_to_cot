
# ADS-B to CoT Gateway Script

This script converts ADS-B data received from aircraft into Cursor on Target (CoT) messages for display in Team Awareness Kit (TAK) applications, such as ATAK or WinTAK. It uses `dump1090` to receive ADS-B data from an RTL-SDR device and processes this data to generate CoT XML messages, which are then sent over UDP to a TAK server or device.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Testing with Fake ADS-B Data](#testing-with-fake-ads-b-data)
- [Customization](#customization)


---

## Overview

The script performs the following functions:

1. **Receives ADS-B Data**: Utilizes `dump1090` to receive ADS-B messages from aircraft using an RTL-SDR device.
2. **Parses SBS Messages**: Processes the ADS-B data in SBS format to extract relevant information.
3. **Generates CoT Messages**: Converts the parsed data into CoT XML messages, including altitude and ICAO codes.
4. **Sends CoT Messages**: Transmits the CoT messages via UDP to a specified TAK device or server.

---

## Features

- **Real-Time Aircraft Tracking**: Displays live positions of aircraft on a TAK map.
- **Altitude and ICAO Labeling**: Includes both altitude and ICAO code with the aircraft icon for enhanced situational awareness.
- **Compatibility with TAK Applications**: Works with ATAK, WinTAK, and other TAK-based systems.
- **Customizable Settings**: Easily configure network settings and display options.

---

## Prerequisites

Before using this script, ensure you have the following:

- **Python 3.6+**: The script is written in Python and requires version 3.7 or higher.
- **RTL-SDR Device**: A compatible USB dongle to receive ADS-B signals.
- **Antenna**: An antenna suitable for 1090 MHz frequency to receive ADS-B broadcasts.
- **\`dump1090\` Software**: A Mode S decoder for RTL-SDR devices.
- **TAK Application**: A TAK client (e.g., ATAK on Android or WinTAK on Windows) configured to receive CoT messages.

---

## Installation

### 1. Clone the Repository

Clone the repository containing the script and `dump1090`:

```bash
git clone https://github.com/jaw1999/adsb-to-cot.git
cd adsb-to-cot



### 2. Build Dump1090

mkdir -p external
cd external
git clone https://github.com/flightaware/dump1090.git
cd ..

cd external/dump1090
make
cd ../../

Configuration

Edit the adsb_to_cot.py script to configure the following settings:

### 1. COT Device Settings

Set the IP address and port of your TAK device or server:

COT_HOST = '192.168.x.x'  # Replace with your TAK device's IP address
COT_PORT = 6969           # Default CoT port; change if necessary

### 2. Network Settings

Confirm the dump1090 Network Settings:

DUMP1090_HOST = '127.0.0.1'  # Usually localhost
DUMP1090_PORT = 30003        # SBS format output port


Usage

1. Connect RTL-SDR Device

    Plug in your RTL-SDR USB dongle.
    Connect the antenna to the RTL-SDR device.
    Position the antenna for optimal ADS-B signal reception.

2. Run the Script

Execute the adsb_to_cot.py script:

python adsb_to_cot.py

3. Monitor Output

    The script will log messages indicating the status.
    It will start dump1090, connect to it, and begin processing ADS-B data.
    CoT messages are sent over UDP to the specified TAK device.

4. Verify in TAK Application

    Open your TAK application on your device.
    Ensure it is configured to receive UDP CoT messages on the port you specified.
    You should see aircraft icons on the map, labeled with their ICAO codes and altitudes.

    Testing with Fake ADS-B Data

If you don't have an RTL-SDR device, you can test the script using fake ADS-B data.

1. Run the Fake ADS-B Data Generator

Use the provided fake_adsb_generator.py script:

python fake_adsb_generator.py


2. Run the Main Script

In another terminal, run the adsb_to_cot.py script:

python adsb_to_cot.py

3. Verify in TAK Application

    The TAK application should display the fake aircraft data.
    This is useful for testing without hardware.


Customization

Adjusting Icon Labels

    Modify the callsign_display in the create_cot_event function to include additional information, such as speed or callsign.

Changing Icon Types

    Adjust the type attribute in the CoT message to represent different types of aircraft or entities.
    Common type codes:
        "a-f-A": Friendly air track (aircraft).
        "a-u-A": Unknown air track (aircraft).
        "a-c-A-f": Civilian fixed-wing aircraft.

Setting Identity and Affiliation

    Change the identity attribute in the <access> element to affect the icon color:
        "friend": Blue
        "hostile": Red
        "neutral": Green
        "unknown": Yellow
