# Install Tempi

1. Preparation
   - Keep RTL-SDR dongle unplugged
   - If setting up a new Pi OS install in "Raspberry Pi Imager" it's preferable to use the following, if you don't need to run a desktop or GUI based apps:
      Operating System → Choose OS → Raspberry Pi OS (other) → Raspberry Pi OS Lite (64-bit)
   - Once your pi boots go to your router's web interface and find the ip address assigned to your pi.
   - It is highly advised to have your router reserve an ip for your pi, otherwise you'll have to lookup the ip each time your pi or router boots.
   - Open a terminal and `ssh <your_ip_address>`

1. Installation
      ```bash
      sudo apt update && sudo apt upgrade && \
         CONFIG_LINE='usb_max_current_enable=1' && \
         if ! grep -q "$CONFIG_LINE" /boot/firmware/config.txt; then echo "$CONFIG_LINE" | sudo tee --append /boot/firmware/config.txt > /dev/null; fi && \
         sudo apt install -y apt-transport-https ca-certificates curl software-properties-common && curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh && \
         echo 'blacklist dvb_usb_rtl28xxu' | sudo tee --append /etc/modprobe.d/blacklist-dvb_usb_rtl28xxu.conf
      ```
1. Power cycle your Raspberry Pi
1. Plug in RTL-SDR Dongle
1. Install notification app on mobile device
   - Open App Store or Google Play
   - Install "Ntfy App"
   - Open the app and subscribe to a topic
     - click + icon
     - Subscribe to topic "tempi"
     - Click "use another server"
     - In the service Url box, replace `"https://ntfy.sh"` with `http://<your_ip_address>`
         <div style="background-color:#DEDBEE; padding: 7px 10px; border-radius: 5px;">
         <h4>NOTE:</h4>
         <ul>
         <li>
            You won't receive tempi push notifications while using mobile data connection. Why?
            Because you just specified an ip address which is only reachable while you are connected to your network.
         </li>
         <li>
            If you need to receive notifications anywhere, you can do so by creating a tunnel which points to your raspberry pi's ip. Recommended tools are <a href="https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/">cloudflared</a> or <a href="https://ngrok.com/docs/getting-started/">ngrok</a>
         </li>
         <li>
            Once the tunnel is established you will have a public url like <code>http://123456.ngrok.io/tempi</code> to which which you can point your Ntfy App.
         </li>
         </div>
1. Run the app -- see the "Run" section in the [main readme](../README.md#run)
