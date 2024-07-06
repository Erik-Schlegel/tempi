import subprocess
import json

MAX_DAILY_MESSAGES = 10

current_day = None
current_data = {}
current_precedent = None

CHANNELS = {
    1: "Music Room",
    2: "Living Room",
    3: "Bedroom",
    4: "Garage",
    5: "Outside",
}

EXAMINED_CHANNELS_LOW_HIGH = (2, 5)


def to_fahrenheit(celsius, decimal_places=1):
    return round((celsius * 9 / 5) + 32, decimal_places)


def is_new_day(data):
    if current_day is None:
        return True
    return current_day != data["time"].split(" ")[0]


def update_day(data):
    global current_day
    current_day = data["time"].split(" ")[0]


def is_current_precedent_changed():
    # print("in is_current_precedent_changed")
    channel_low = current_data.get(EXAMINED_CHANNELS_LOW_HIGH[0])
    channel_high = current_data.get(EXAMINED_CHANNELS_LOW_HIGH[1])
    if current_precedent is None or channel_low is None or channel_high is None:
        # print("unknown precedent or not enough data to determine temperature precedent")
        return False
    else:
        # print("temperature precedent changed")
        return current_precedent != (channel_low["Temp"] > channel_high["Temp"])


def update_current_precedent(status="init"):
    # print("in update_current_precedent")
    # print("status", status)

    global current_precedent
    # print("current_precedent before", current_precedent)
    channel_low = current_data.get(EXAMINED_CHANNELS_LOW_HIGH[0])
    channel_high = current_data.get(EXAMINED_CHANNELS_LOW_HIGH[1])
    if channel_low is None or channel_high is None:
        print("Cannot update precedent due to missing data")
        return

    current_precedent = channel_low["Temp"] > channel_high["Temp"]
    # print("current_precedent after", current_precedent)


def main():
    previous_data_in = None
    message_count = 0

    process = subprocess.Popen(
        ["rtl_433", "-f", "915000000", "-F", "json"],
        stdout=subprocess.PIPE,
        # stderr=subprocess.DEVNULL,  # Redirect stderr to suppress messages
    )

    print("\n")

    try:
        # Indefinite loop reads input data from rtl_433
        for line in iter(process.stdout.readline, b""):
            # data: {
            # 'time': '2024-06-27 13:27:14',
            # 'model': 'AmbientWeather-WH31E',
            # 'id': 43,
            # 'channel': 2,
            # 'battery_ok': 1,
            # 'temperature_C': 24.4,
            # 'humidity': 41,
            # 'data': 'c100000000',
            # 'mic': 'CRC'
            # }
            data = json.loads(line.decode("utf-8"))

            # The same data signal is sent 2x by each sensor.
            if data == previous_data_in:
                continue
            previous_data_in = data

            # add/update data in current_data. Size constrained to the CHANNELS defined above.
            # current_data: {
            #   1: {'Room': 'Music Room', 'Temp': 79.0, 'H20': 40},
            #   2: {'Room': 'Living Room', 'Temp': 79.0, 'H20': 40},
            #   3: {'Room': 'Bedroom', 'Temp': 79.0, 'H20': 40},
            #   4: {'Room': 'Garage', 'Temp': 83.3, 'H20': 36},
            #   5: {'Room': 'Outside', 'Temp': 85.8, 'H20': 32},
            # }
            current_data[data["channel"]] = {
                "Room": CHANNELS[data["channel"]],
                "Temp": to_fahrenheit(data["temperature_C"]),
                "H20": data["humidity"],
            }

            print("\033c", end="")  # clear the screen
            for channel in CHANNELS:
                if channel in current_data:
                    print(
                        f"{current_data[channel]['Room']}: {current_data[channel]['Temp']}F, {current_data[channel]['H20']}%"
                    )
                else:
                    print(f"{CHANNELS[channel]}: No data")

            print("\n")

            if is_new_day(data):
                message_count = 0
                update_day(data)

            if current_precedent is None:
                update_current_precedent("initializing")
                continue

            if is_current_precedent_changed():
                update_current_precedent("actual")
                if current_precedent and message_count < MAX_DAILY_MESSAGES:
                    message = f"{CHANNELS[EXAMINED_CHANNELS_LOW_HIGH[0]]} is {'warmer' if current_precedent else 'cooler'} than {CHANNELS[EXAMINED_CHANNELS_LOW_HIGH[1]]}"

                    subprocess.run(
                        [
                            "curl",
                            "-d",
                            "lr's warmer than outside",
                            "localhost/tempi",
                        ]
                    )

                    print(
                        f"{CHANNELS[EXAMINED_CHANNELS_LOW_HIGH[0]]} is warmer than {CHANNELS[EXAMINED_CHANNELS_LOW_HIGH[1]]}"
                    )
                else:
                    subprocess.run(
                        [
                            "curl",
                            "-d",
                            "lr's cooler than outside",
                            "localhost/tempi",
                        ]
                    )
                    print(
                        f"{CHANNELS[EXAMINED_CHANNELS_LOW_HIGH[0]]} is cooler than {CHANNELS[EXAMINED_CHANNELS_LOW_HIGH[1]]}"
                    )
                message_count += 1

    except Exception as ex:
        print(ex)


if __name__ == "__main__":
    main()
