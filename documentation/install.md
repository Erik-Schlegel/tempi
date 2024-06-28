# Install

1. Prep
   - Keep RTL-SDR dongle unplugged
   - Update system
      ```sh
      sudo apt update
      sudo apt upgrade
      ```
    - Setup Bluetooth Stuff (optional, for FM testing)
      ```sh
      bluetoothctl
      power on
      agent on
      default-agent
      scan on
      # wait for target device to show
      # e.g. Raycons -- 98:47:44:33:97:DF
      pair <_mac_address_>
      trust <_mac_address_> #allow auto-reconnect
      connect <_mac_address_>
      scan off
      quit
      ```
2. Setup Drivers & Software
   - Run these lines individually:
      ```sh
      # Remove conflicting drivers
      echo 'usb_max_current_enable=1' | sudo tee --append /boot/firmware/config.txt
      sudo apt purge ^librtlsdr
      sudo rm -rvf /usr/lib/librtlsdr* /usr/include/rtl-sdr* /usr/local/lib/librtlsdr* /usr/local/include/rtl-sdr* /usr/local/include/rtl_* /usr/local/bin/rtl_*

      # Install RTL-SDR Drivers
      sudo apt install libusb-1.0-0-dev git cmake pkg-config build-essential libtool autoconf python3

      git clone https://github.com/rtlsdrblog/rtl-sdr-blog
      cd rtl-sdr-blog && mkdir build && cd build
      cmake ../ -DINSTALL_UDEV_RULES=ON
      make
      sudo make install
      sudo cp ../rtl-sdr.rules /etc/udev/rules.d/
      sudo ldconfig
      echo 'blacklist dvb_usb_rtl28xxu' | sudo tee --append /etc/modprobe.d/blacklist-dvb_usb_rtl28xxu.conf

      cd ~/
      git clone https://github.com/merbanan/rtl_433.git
      cd rtl_433/ && mkdir build && cd build
      cmake ..
      make
      sudo make install
      ```
3. Test
   - Power cycle device
   - Plug in RTL-SDR dongle
   - **Test Data Decryption**
      `rtl_433 -f 915000000 -F json` should take ~ 15 seconds at most for data to show.
   - **Test FM (optional)** Attempt to play local FM station, e.g. 90.1 FM.
      ```sh
      rtl_fm -f 90.1M -M wfm -s 2400000 -r 96000 | aplay -r 96000 -f S16_LE
      ```
