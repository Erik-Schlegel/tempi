# Install

1. Prep
   - Keep RTL-SDR dongle unplugged
   - If setting up a new Pi OS install in "Raspberry Pi Imager" it's preferable to use:
      Operating System > Choose OS > Raspberry Pi OS (other) > Raspberry Pi OS Lite (64-bit)
   - Once the device is booted go to your router's web interface and find the ip address assigned to your pi.
   - open a terminal and `ssh <ip_address_here>`
   - Update system
      ```sh
      sudo apt update
      sudo apt upgrade
      ```
   - Increase max current supplied to usb devices.
      ```sh
      CONFIG_LINE='usb_max_current_enable=1'
      if ! grep -q "$CONFIG_LINE" /boot/firmware/config.txt; then
        echo "$CONFIG_LINE" | sudo tee --append /boot/firmware/config.txt > /dev/null
      fi
      ```
2. Setup Drivers & Software
   - Run these lines individually:
      ```sh
      # Remove default drivers which are known to conflict
      sudo apt purge ^librtlsdr
      sudo rm -rvf /usr/lib/librtlsdr* /usr/include/rtl-sdr* /usr/local/lib/librtlsdr* /usr/local/include/rtl-sdr* /usr/local/include/rtl_* /usr/local/bin/rtl_*

      # Install RTL-SDR Requirements
      sudo apt install -y libusb-1.0-0-dev git cmake pkg-config build-essential libtool autoconf
      git clone https://github.com/rtlsdrblog/rtl-sdr-blog
      cd rtl-sdr-blog && mkdir build && cd build
      cmake ../ -DINSTALL_UDEV_RULES=ON
      make
      sudo make install
      sudo cp ../rtl-sdr.rules /etc/udev/rules.d/
      sudo ldconfig
      echo 'blacklist dvb_usb_rtl28xxu' | sudo tee --append /etc/modprobe.d/blacklist-dvb_usb_rtl28xxu.conf

      # Install rtl_433--a project which decodes rf data signals.
      cd ~/
      git clone https://github.com/merbanan/rtl_433.git
      cd rtl_433/ && mkdir build && cd build
      cmake ..
      make
      sudo make install

      # Install Software to run Tempi and do notifications
      sudo apt install -y python3 docker.io
      sudo mkdir /etc/ntfy
      sudo wget -P /etc/ntfy https://raw.githubusercontent.com/binwiederhier/ntfy/main/server/server.yml
      sudo nano /etc/ntfy/server.yml

      # modify two lines:
      # uncomment base-url
      # set base-url value to: http://<yourip>
      # upstream-base-url
      # close server.yml
      ```
3. Install notification app on mobile device
   - Open App Store or Google Play
   - Search for and install Ntfy app
   - Go to settings and set default server to 192.168.1.22
   - Subscribe to the "tempi" topic


   ```sh
      #sudo docker run -p 80:80 -td binwiederhier/ntfy serve
      sudo docker run -v /var/cache/ntfy:/var/cache/ntfy -v /etc/ntfy:/etc/ntfy -p 80:80 binwiederhier/ntfy serve --cache-file /var/cache/ntfy/cache.db

      # To see what docker containers are running
      sudo docker ps

      # To see all docker containers running or not
      sudo docker ps -a

      # To stop a docker container
      sudo docker stop <container_id>

      # To stop all docker containers
      sudo docker stop $(sudo docker ps -q)

      # To see any error logs for a particular container
      sudo docker logs <container_id>
      ```
4. Test
   - Power cycle device
   - Plug in RTL-SDR dongle
   - **Test Data Decryption**
      `rtl_433 -f 915000000 -F json` should take ~ 15 seconds at most for data to show.
   - **Test FM (optional)** Attempt to play local FM station, e.g. 90.1 FM.
      ```sh
      rtl_fm -f 90.1M -M wfm -s 2400000 -r 96000 | aplay -r 96000 -f S16_LE
      ```

5. Make ntfy message available externally
   - The above creates a setup which notifies devices only when they're connected to the same network. e.g.: Client devices running ntfy connect directly to the local ip.
   - To make notifications available externally, we'll set up a [cloudflare tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/).
   - This involves:
     - installing docker on the server to which messages will be published
     - logging in to cloudflare and creating a 'cloudflared tunnel' installed with docker.
     - installing the docker image (cmd is created by cloudflare)
     - running the
