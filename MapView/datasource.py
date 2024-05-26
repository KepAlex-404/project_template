import asyncio
import json
from datetime import datetime
import websockets
from kivy import Logger
from pydantic import BaseModel, field_validator
import scipy.signal
from config import STORE_HOST, STORE_PORT

class ProcessedAgentData(BaseModel):
    road_state: str
    user_id: int
    x: float
    y: float
    z: float
    latitude: float
    longitude: float
    timestamp: datetime

    @classmethod
    @field_validator("timestamp", mode="before")
    def check_timestamp(cls, value):
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value)
        except (TypeError, ValueError):
            raise ValueError(
                "Invalid timestamp format. Expected ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)."
            )

class Datasource:
    def __init__(self, user_id=1):
        self.user_id = user_id
        self.connection_status = None
        self._new_data = []
        asyncio.ensure_future(self.connect_to_server())

    async def connect_to_server(self):
        uri = f"ws://{STORE_HOST}:{STORE_PORT}/ws/{self.user_id}"
        while True:
            Logger.debug("CONNECT TO SERVER")
            async with websockets.connect(uri) as websocket:
                self.connection_status = "Connected"
                try:
                    while True:
                        data = await websocket.recv()
                        try:
                            parsed_data = json.loads(data)
                            self.handle_received_data(parsed_data)
                        except json.JSONDecodeError:
                            print("Received data is not valid JSON:")
                            print(data)
                except websockets.ConnectionClosedOK:
                    self.connection_status = "Disconnected"
                    Logger.debug("SERVER DISCONNECT")

    def handle_received_data(self, data):
        # Update your UI or perform actions with received data here
        Logger.debug(f"Received data: {data}")
        sorted_data = [
                ProcessedAgentData(**processed_data_json)
                for processed_data_json in json.loads(data)
            ]
        self._new_data.extend(sorted_data)
        
    def get_new_data(self):
        return self._new_data