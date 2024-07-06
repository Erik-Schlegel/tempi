#!/bin/sh

sudo apt update &&
  sudo apt upgrade -y &&
  CONFIG_LINE='usb_max_current_enable=1' &&
  if ! grep -q "$CONFIG_LINE" /boot/firmware/config.txt; then echo "$CONFIG_LINE" | sudo tee --append /boot/firmware/config.txt >/dev/null; fi &&
  echo 'blacklist dvb_usb_rtl28xxu' | sudo tee --append /etc/modprobe.d/blacklist-dvb_usb_rtl28xxu.conf &&
  echo 'Reboot to apply changes'
