# First stage: Build
FROM alpine:latest AS build
WORKDIR /tempi

# Install dependencies
RUN apk update && apk add --no-cache \
  git \
  cmake \
  build-base \
  libtool \
  libusb-dev \
  autoconf \
  pkgconfig \
  python3 \
  py3-pip \
  linux-headers

# Remove conflicting drivers
RUN rm -rvf /usr/lib/librtlsdr* /usr/include/rtl-sdr* && \
  rm -rvf /usr/local/lib/librtlsdr* /usr/local/include/rtl-sdr* && \
  rm -rvf /usr/local/include/rtl_* /usr/local/bin/rtl_*

# Build RTL-SDR
RUN git clone https://github.com/rtlsdrblog/rtl-sdr-blog && \
  cd rtl-sdr-blog && \
  mkdir build && cd build && \
  cmake ../ -DINSTALL_UDEV_RULES=ON && \
  make && \
  make install && \
  cp ../rtl-sdr.rules /etc/udev/rules.d/ && \
  echo 'blacklist dvb_usb_rtl28xxu' >> /etc/modprobe.d/blacklist-dvb_usb_rtl28xxu.conf

# Build rtl_433
RUN git clone https://github.com/merbanan/rtl_433.git && \
  cd rtl_433 && \
  mkdir build && cd build && \
  cmake .. && \
  make && \
  make install

# Second stage: Minimal runtime
FROM alpine:latest
WORKDIR /tempi

# Copy the build artifacts from the first stage
COPY --from=build /usr/local /usr/local
COPY --from=build /etc/udev/rules.d/rtl-sdr.rules /etc/udev/rules.d/rtl-sdr.rules
COPY --from=build /etc/modprobe.d/blacklist-dvb_usb_rtl28xxu.conf /etc/modprobe.d/blacklist-dvb_usb_rtl28xxu.conf

# Install runtime dependencies
RUN apk update && apk add --no-cache \
  python3 \
  py3-pip \
  libusb

# Copy the application files
COPY . /tempi

CMD ["python3", "tempi.py"]
