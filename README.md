# Tempi

## Description

 Monitors multiple hyper-local rf-based weather stations (e.g. [Ambient Weather](https://www.amazon.com/Ambient-Weather-WS-3000-X5-Thermo-Hygrometer-Controlled/dp/B01IPOESHI)). Sends two push notifications daily:
1. When station A's temperature exceeds station B's temp
2. When station A's temperature drops below station B's temp by a configurable amount (measured in Fahrenheit).

## Example Application
This is useful information in warm weather. It is more cost effective to run a whole-house fan than AC, but knowing when to turn off the AC and turn on the fan takes (ugh) effort. Here at Eschware are not lazy; we're "efficient".

## Hardware
Designed to be run on a raspberry pi with a [RTL-SDR](https://www.amazon.com/RTL-SDR-Blog-RTL2832U-Software-Defined/dp/B0CD7558GT).


## Setup

[Software Install](./documentation/install.md)