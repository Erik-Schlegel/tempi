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
See startup instructions at [dockerhub](https://hub.docker.com/r/eschware/tempi)

## Development

Changing things like the channel names, etc, is done by passing variables in to the docker container, you'll see them in the script on dockerhub. Now, if you're me (esch) you'll rest a little easier when you remember you've created tempi launcher script in bin-private. Using that you can:


```sh
tempi stop # this stops any previous running instance.
tempi iterate 1.#.# # Allows for dev change -> rebuild -> launch loops.
# at this point the container is running with the latest code. Check it with <ip>:8081
```

When dev is complete:
```sh
tempi stop
tempi build 1.#.#
tempi deploy 1.#.# # this pushes the image to dockerhub.
tempi prod # this restarts the container with latest in dockerhub.
```
