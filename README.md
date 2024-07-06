# Tempi

## Description

App to monitor multiple rf-based weather stations (e.g. [Ambient Weather](https://www.amazon.com/Ambient-Weather-WS-3000-X5-Thermo-Hygrometer-Controlled/dp/B01IPOESHI)). and sends push notifications when:
1. Station A's temperature exceeds station B
2. Station B's temperature exceeds station A

## But, why?
It's expensive to run AC. Yet, proactively staying on top of things and consistently monitoring the weather takes discipline and focus. And while we're not easily distracted or anything, usually, it's hard to *SQUIRREL!!* ...push notifications are easier.

## Hardware
Designed to be run on a Raspberry pi with a RTL-SDR dongle. See [prerequisites](./documentation/prerequisites.md)

## Setup
[Software Install](./documentation/install.md)

## Run

```bash
# Determine the device id of the RTL-SDR device
lsub

# This will output something like:
# Bus 001 Device 002: ID 0bda:2838 Realtek Semiconductor Corp. RTL2838 DVB-T
# Pass 001/002 in to the docker run call:
sudo docker run --device=/dev/bus/usb/001/002 esch:arm64
```