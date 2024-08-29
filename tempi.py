import os
import ast
import subprocess
import json
from datetime import datetime
from zoneinfo import ZoneInfo
import traceback
from measurement_table import MeasurementTable
from logger import create_logger

CHANNELS = ast.literal_eval(os.getenv('CHANNELS'))
LOW_TEMP_DESIRED_CHANNEL = os.getenv("LOW_TEMP_DESIRED_CHANNEL")
HIGH_TEMP_EXPECTED_CHANNEL = os.getenv("HIGH_TEMP_EXPECTED_CHANNEL")

TIME_ZONE_ID = os.getenv("TIME_ZONE_ID")

current_day = None
current_data = {}
temperature_precedent = None

logger = create_logger("tempi_logger", "tempi.log")



def notify(message):
    try:
        subprocess.run(
            ["curl", "-X", "POST", "-d", message, "http://localhost:8080/tempi"],
            check=True
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Error in notify: {e.stderr}")


def update_api_data(data):
    try:
        value = json.dumps(data)
        subprocess.run(
            ["curl", "-X", "UPDATE", "-H", "Content-Type: application/json", "-d", value, "http://localhost:8000/data"],
            check=True
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Error in update_api_data: {e.stderr}")


def to_fahrenheit(celsius, decimal_places=1):
    return round((celsius * 9 / 5) + 32, decimal_places)


def is_new_day(data):
    if current_day is None:
        return True
    return current_day != data["time"].split(" ")[0]


def update_day(data):
    global current_day
    current_day = data["time"].split(" ")[0]


def is_temperature_precedent_changed():
    channel_low = current_data.get(LOW_TEMP_DESIRED_CHANNEL)
    channel_high = current_data.get(HIGH_TEMP_EXPECTED_CHANNEL)
    if temperature_precedent is None or channel_low is None or channel_high is None:
        return False
    else:
        return temperature_precedent != (channel_low["Temp"] > channel_high["Temp"])


def update_temperature_precedent():
    global temperature_precedent

    channel_low = current_data.get(LOW_TEMP_DESIRED_CHANNEL)
    channel_high = current_data.get(HIGH_TEMP_EXPECTED_CHANNEL)
    if channel_low is None or channel_high is None:
        print("Cannot update precedent due to missing data")
        return

    temperature_precedent = channel_low["Temp"] > channel_high["Temp"]


def get_current_time():
    return datetime.now(ZoneInfo(TIME_ZONE_ID)).isoformat()


def main():
    notify(f"Tempi Started at { get_current_time() }")

    previous_data_in = None
    message_count = 0

    try:
        logger.debug("Creating MeasurementTable instance")
        measurementTable = MeasurementTable()
    except Exception as ex:
        logger.error(f"Error in main: {ex}")

    process = subprocess.Popen(
        ["rtl_433", "-f", "915000000", "-F", "json"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    print("\n")

    # Continuous loop. Reads input data from rtl_433
    for line in iter(process.stdout.readline, b""):
        try:
            data = json.loads(line.decode("utf-8"))
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

            # Stations sync clocks daily; channel data is not present in this signal. Ignore the signal.
            # And, separate issue: the same data signal is always sent 2x by each sensor. Ignore the dupe.
            if data == previous_data_in or not data["channel"]:
                continue

            previous_data_in = data

            fahrenheit = to_fahrenheit(data["temperature_C"])

            current_data[data["channel"]] = {
                "Location": CHANNELS[data["channel"]],
                "Temp": fahrenheit,
                "H20": data["humidity"],
            }

            current_data["current_time"] = get_current_time()
            # TODO: Move example of current_data to documentation.
            # current_data: {
            #   current_time: '2024-06-27T13:27:14.123456-07:00',
            #   1: {'Location': 'Outside', 'Temp': 85.8, 'H20': 32},
            #   2: {'Location': 'Bedroom', 'Temp': 79.0, 'H20': 40},
            #   4: {'Location': 'Garage', 'Temp': 83.3, 'H20': 36},
            #   5: {'Location': 'Living Room', 'Temp': 79.0, 'H20': 40},
            # }

            update_api_data(current_data)
            measurementTable.add_measurement(current_data["current_time"], data["channel"], fahrenheit, data["humidity"])

            print("\033c", end="")  # clear the screen
            for channel in CHANNELS:
                if channel in current_data:
                    print(
                        f"{current_data[channel]['Location']}: {current_data[channel]['Temp']}F, {current_data[channel]['H20']}%"
                    )
                else:
                    print(f"{CHANNELS[channel]}: No data")

            print("\n")

            if is_new_day(data):
                message_count = 0
                update_day(data)

            if temperature_precedent is None:
                update_temperature_precedent()
                continue

            if is_temperature_precedent_changed():
                update_temperature_precedent()
                message = f"{CHANNELS[LOW_TEMP_DESIRED_CHANNEL]} is {'warmer' if temperature_precedent else 'cooler'} than {CHANNELS[HIGH_TEMP_EXPECTED_CHANNEL]}"
                notify(message)
                print(message)

        except Exception as ex:
            error_message = ''.join(traceback.format_exception(None, ex, ex.__traceback__))
            logger.error(f"Error in main: {error_message}")


if __name__ == "__main__":
    main()
