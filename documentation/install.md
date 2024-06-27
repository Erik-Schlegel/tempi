# Install


1. Prep
   - Keep RTL-SDR dongle unplugged
   - Run these lines individually:
      ```sh
      sudo apt update
      sudo apt upgrade
      ```
2. Drivers & Software
   - Run these lines individually:
      ```sh
      # Remove conflicting drivers
      echo 'usb_max_current_enable=1' | sudo tee --append /boot/firmware/config.txt
      sudo apt purge ^librtlsdr
      sudo rm -rvf /usr/lib/librtlsdr* /usr/include/rtl-sdr* /usr/local/lib/librtlsdr* /usr/local/include/rtl-sdr* /usr/local/include/rtl_* /usr/local/bin/rtl_*

      # Install RTL-SDR Drivers
      sudo apt install libusb-1.0-0-dev git cmake pkg-config build-essential libtool autoconf

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
   - Setup Bluetooth Stuff
      ```sh
      bluetoothctl
      power on
      agent on
      default-agent
      scan on
      # wait for device to show e.g. Raycons -- 98:47:44:33:97:DF
      pair 98:47:44:33:97:DF
      trust 98:47:44:33:97:DF #allow auto-reconnect in future
      connect 98:47:44:33:97:DF
      scan off
      quit
   ```
   - Plug in RTL-SDR dongle
   - **Test FM** Attempt to play a strong local FM station, e.g. 90.1 FM.
      ```sh
      rtl_fm -f 90.1M -M wfm -s 2400000 -r 96000 | aplay -r 96000 -f S16_LE

      # rtl_fm only plays mono. want to test stereo?
      sudo apt install sox
      rtl_fm -f 90.1M -M wfm -s 2400000 -r 96000 - | sox -t raw -r 96000 -e signed -b 16 -c 1 -V1 - -r 96000 -c 2 -t wav - | aplay -r 96000 -f S16_LE
      ```
   - **Test Data Decryption**
   - `rtl_433 -f 915000000` should take ~ 15 seconds at most for data to show.


----
Unworking but unnecessary.
6. Enable VNC
   ```sh
   sudo raspi-config # Interface options > VNC Enable/Disable > Yes
   # Install and run 'VncViewer' on another system
   ```
7. Launch gqrx from VNC (it's a GUI app) -- make sure to select the RTLSDR BLOG device