import importlib
import io
import json
import logging
import os
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

os.environ.setdefault("CHANNELS", "{1: 'Patio', 2: 'Desk'}")
os.environ.setdefault("LOW_TEMP_DESIRED_CHANNEL", "2")
os.environ.setdefault("HIGH_TEMP_EXPECTED_CHANNEL", "1")
os.environ.setdefault("TIME_ZONE_ID", "America/Los_Angeles")
with patch("logging.FileHandler", return_value=logging.NullHandler()):
    tempi = importlib.import_module("tempi")


class PrecedentNotificationTests(unittest.TestCase):
    def test_messages_name_whichever_sensor_becomes_warmer(self):
        readings = [
            {"channel": 1, "temperature_C": 20, "humidity": 40},
            {"channel": 2, "temperature_C": 21, "humidity": 40},
            {"channel": 2, "temperature_C": 18, "humidity": 40},
            {"channel": 2, "temperature_C": 22, "humidity": 40},
        ]
        lines = b"".join(json.dumps({"time": "2026-09-30 12:00:00", **r}).encode() + b"\n" for r in readings)

        class FakeProcess:
            stdout = io.BytesIO(lines)

        class FakeTable:
            def add_measurement(self, *args):
                pass

        notifications = []
        with patch.object(tempi, "CHANNELS", {1: "Patio", 2: "Desk"}), \
             patch.object(tempi, "LOW_TEMP_DESIRED_CHANNEL", 2), \
             patch.object(tempi, "HIGH_TEMP_EXPECTED_CHANNEL", 1), \
             patch.object(tempi, "MeasurementTable", return_value=FakeTable()), \
             patch.object(tempi.subprocess, "Popen", return_value=FakeProcess()), \
             patch.object(tempi, "update_api_data"), \
             patch.object(tempi, "notify", side_effect=notifications.append), \
             redirect_stdout(io.StringIO()):
            tempi.current_day = None
            tempi.current_data = {}
            tempi.temperature_precedent = None
            tempi.main()

        self.assertEqual(notifications[1:], ["Patio is warmer", "Desk is warmer"])


if __name__ == "__main__":
    unittest.main()
