# Tempi

## Description

Monitor multiple rf-based weather stations (e.g. [Ambient Weather](https://www.amazon.com/Ambient-Weather-WS-3000-X5-Thermo-Hygrometer-Controlled/dp/B01IPOESHI)), and send push notifications when:
1. Station A's temperature exceeds station B (e.g. it's hotter outside)
2. Station B's temperature exceeds station A (e.g. it's hotter inside)

## But, why?
It's expensive to run AC. Yet, proactively and consistently monitoring the temperature situation takes discipline. And while we're not easily distracted or anything, usually, it's hard to ***SQUIRREL!*** ...it's just easier to get a push notification.

## Hardware
See [prerequisites](./documentation/prerequisites.md)


## Setup
See [Software Install](./documentation/install.md)


## Run
```bash
# Determine the device id of the RTL-SDR device, by listing the usb devices:
lsusb

# That will output multiple lines with something like:      Bus 001 Device 002 [...] RTL2838 DVB-T
# We need to pass that <bus#>/<device#> info along when we start the app. Given Bus 001 Device 002:
sudo docker run -p 80:80 --device=/dev/bus/usb/001/002 -d eschware/tempi:latest
```