# First stage: Build
FROM ubuntu:latest AS build
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /tempi

RUN echo 'starting build...' && \
  # Environment preparation
  apt update && \
  apt upgrade -y && \
  apt install -y \
  git \
  docker.io \
  python3 \
  cmake \
  pkg-config \
  build-essential \
  libtool \
  libusb-1.0-0-dev \
  autoconf && \
  # Remove drivers which conflict with RTL_SDR
  apt purge -y ^librtlsdr && \
  rm -rvf /usr/lib/librtlsdr* /usr/include/rtl-sdr* && \
  rm -rvf /usr/local/lib/librtlsdr* /usr/local/include/rtl-sdr* && \
  rm -rvf /usr/local/include/rtl_* /usr/local/bin/rtl_* && \
  # Build RTL-SDR
  cd /tempi && \
  git clone https://github.com/rtlsdrblog/rtl-sdr-blog && \
  cd rtl-sdr-blog && mkdir build && cd build && \
  cmake ../ -DINSTALL_UDEV_RULES=ON && \
  make && \
  make install && \
  cp ../rtl-sdr.rules /etc/udev/rules.d/ && \
  ldconfig && \
  mkdir -p /etc/modprobe.d && \
  echo 'blacklist dvb_usb_rtl28xxu' | tee --append /etc/modprobe.d/blacklist-dvb_usb_rtl28xxu.conf && \
  # Build rtl_433
  cd /tempi && \
  git clone https://github.com/merbanan/rtl_433.git && \
  cd rtl_433/ && mkdir build && cd build && \
  cmake .. && \
  make && \
  make install && \
  # START: Cleanup
  apt clean && \
  rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /tempi/rtl-sdr-blog /tempi/rtl_433


# Second stage: Minimal runtime
FROM ubuntu:latest
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /tempi

# Copy the build artifacts from the first stage
COPY --from=build /usr/local /usr/local
COPY --from=build /etc/udev/rules.d/rtl-sdr.rules /etc/udev/rules.d/rtl-sdr.rules
COPY --from=build /etc/modprobe.d/blacklist-dvb_usb_rtl28xxu.conf /etc/modprobe.d/blacklist-dvb_usb_rtl28xxu.conf

# Install runtime dependencies
RUN apt update && \
  apt upgrade -y && \
  apt install -y \
  python3 \
  libusb-1.0-0 && \
  apt clean && \
  rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy the application files
COPY . /tempi

CMD ["python3", "tempi.py"]