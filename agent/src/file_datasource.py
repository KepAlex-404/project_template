from csv import DictReader
from datetime import datetime
from contextlib import contextmanager

from domain.aggregated_data import AggregatedData
from marshmallow import Schema

from schema.accelerometer_schema import AccelerometerSchema
from schema.gps_schema import GpsSchema

import config


class FileDataSource:
    def __init__(self) -> None:
        self.readers = {
            'GPS': CSVReader('data/gps.csv', GpsSchema()),
            'ACCELEROMETER': CSVReader(
                'data/accelerometer.csv', AccelerometerSchema()
            ),
        }

    def read(self) -> AggregatedData:
        try:
            acc = self.readers['ACCELEROMETER'].read()
            gps = self.readers['GPS'].read()
            ts = datetime.now()
            user_id = config.USER_ID
            return AggregatedData(
                user_id=user_id, accelerometer=acc, gps=gps, timestamp=ts
            )
        except Exception as e:
            print(f"Error: {e}")

    @contextmanager
    def start_reading(self):
        try:
            for reader in self.readers.values():
                reader.start_reading()
            yield
        finally:
            self.stop_reading()
                
    def stop_reading(self):
        for reader in self.readers.values():
            reader.stop_reading()


class CSVReader:
    def __init__(self, filename, schema: Schema):
        self.filename = filename
        self.schema = schema
        self.file = None
        self.reader = None

    def start_reading(self):
        self.file = open(self.filename, "r")
        self.reader = DictReader(self.file)
        return self.reader

    def read(self):
        row = next(self.reader, None)

        if row is None:
            self.file.seek(0)
            row = next(self.reader, None)

        return self.schema.load(row)

    def stop_reading(self):
        if self.file:
            self.file.close()
