import os
import sqlite3
import logging
from contextlib import contextmanager


class MeasurementTable:
    logging.basicConfig(filename='/log/measurement_table.log', level=logging.DEBUG, format='%(levelname)s - %(message)s')

    _instance = None


    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MeasurementTable, cls).__new__(cls, *args, **kwargs)
        return cls._instance


    def __init__(self):
        """
        Initializes the MeasurementTable object.

        This method sets up the connection to the SQLite database and creates the measurements table if it doesn't exist.

        Parameters:
            None

        Returns:
            None
        """

        if not hasattr(self, "initialized"):
            self.connection = None
            self.cursor = None

            TABLE_PATH = "/data/tempi.db"

            if not os.path.exists(TABLE_PATH):
                self.connection = sqlite3.connect(TABLE_PATH)
                self.cursor = self.connection.cursor()
                self.cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS measurements (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        datetime DATETIME,
                        channel INTEGER,
                        fahrenheit REAL,
                        humidity REAL
                    )
                    """
                )
                self.connection.commit()
            else:
                self.connection = sqlite3.connect(TABLE_PATH)
                self.connection.row_factory = sqlite3.Row # Return rows as dictionaries
                self.cursor = self.connection.cursor()

            self.initialized = True


    @contextmanager
    def _get_cursor(self):
        try:
            cursor = self.connection.cursor()
            yield cursor
            self.connection.commit()
        except sqlite3.Error as e:
            self.connection.rollback()
            logging.error(f"Error: {e}")
            raise e
        finally:
            cursor.close()


    def add_measurement(self, datetime: str, channel:int, fahrenheit:float, humidity:float):
        """
        Add a measurement to the database.
        Parameters:
        - datetime (str): The datetime of the measurement in ISO 8601 format (e.g. "2024-08-12 21:50:48")
        - channel (int): The channel number of the sensor.
        - fahrenheit (float): The temperature in Fahrenheit.
        - humidity (float): The humidity level.
        Raises:
        - sqlite3.Error: If there is an error executing the SQL statements.
        """

        with self._get_cursor() as cursor:

            cursor.execute("BEGIN TRANSACTION")

            try:
                cursor.execute(
                    """
                    INSERT INTO measurements (datetime, channel, fahrenheit, humidity)
                    VALUES (?, ?, ?, ?)
                    """,
                    (datetime, channel, fahrenheit, humidity)
                )

                cursor.execute(
                    """
                    DELETE FROM measurements WHERE datetime < datetime('now', '-1 day')
                    """
                )

                cursor.execute("COMMIT")

            except sqlite3.Error as e:
                cursor.execute("ROLLBACK")
                logging.error(f"Error: {e}")
                raise e


    def get_historical_temps(self, channel: int, duration_minutes:int, interval_minutes:int):
        """
        Returns a list of temperature readings over a given duration, averaged at intervals.

        :param channel: The sensor's channel number.
        :param duration_minutes: Number of minutes to look back in time.
        :param interval_minutes: Number of minutes to average temperature readings in duration. Data point granularity.
        """

        with self._get_cursor() as cursor:

            try:
                cursor.execute(
                    """
                    SELECT
                        datetime,
                        ROUND(AVG(fahrenheit), 1) AS fahrenheit
                    FROM
                        measurements
                    WHERE
                        channel = ? AND
                        datetime >= datetime('now', ?)
                    GROUP BY
                        strftime('%s', datetime) / ?
                    ORDER BY
                        datetime ASC
                    """,
                    (channel, f"-{duration_minutes} minutes", interval_minutes * 60)
                )

                rows = cursor.fetchall()
                return [dict(row) for row in rows]

            except sqlite3.Error as e:
                logging.error(f"Error: {e}")
                raise e

