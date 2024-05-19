from atexit import register
from datetime import datetime
from json import loads, JSONDecodeError
from os import makedirs
from os.path import abspath, exists
from time import sleep
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from leads import require_config, L, DataContainer
from leads.comm import Service, Client, start_client, create_client, Callback, Connection, ConnectionBase
from leads.data_persistence import DataPersistence, Vector, CSV, DEFAULT_HEADER

config = require_config()
if not exists(config.data_dir):
    L.debug(f"Data directory not found. Creating \"{abspath(config.data_dir)}\"...")
    makedirs(config.data_dir)

data_record: DataPersistence[DataContainer] = DataPersistence(1, compressor=lambda o, s: o[-s:])
time_stamp_record: DataPersistence[int] = DataPersistence(2000)
speed_record: DataPersistence[float] = DataPersistence(2000)
acceleration_record: DataPersistence[float] = DataPersistence(2000)
voltage_record: DataPersistence[float] = DataPersistence(2000)
gps_record: DataPersistence[Vector[float]] = DataPersistence(2000)
csv = CSV(f"{config.data_dir}/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv", DEFAULT_HEADER,
          time_stamp_record, voltage_record, speed_record)


def retry(service: Service) -> Client:
    L.warn("Retrying connection...")
    return start_client(config.comm_addr, create_client(service.port(), callback), True)


class CommCallback(Callback):
    def __init__(self) -> None:
        super().__init__()
        self.client: Client = start_client(config.comm_addr, create_client(config.comm_port, self), True)

    def on_connect(self, service: Service, connection: Connection) -> None:
        self.super(service=service, connection=connection)
        L.info("Connected")

    def on_fail(self, service: Service, error: Exception) -> None:
        self.super(service=service, error=error)
        L.error(f"Comm client error: {repr(error)}")
        sleep(10)
        assert isinstance(service, Client)
        self.client = retry(service)

    def on_receive(self, service: Service, msg: bytes) -> None:
        self.super(service=service, msg=msg)
        try:
            d = loads(msg.decode())
            data_record.append(d)
            acceleration_record.append(Vector(d["forward_acceleration"], d["lateral_acceleration"]))
            gps_record.append(Vector(d["latitude"], d["longitude"]))
            if config.save_data:
                csv.write_frame(*(d[key] for key in csv.header()))
            else:
                time_stamp_record.append(int(d["t"]))
                speed_record.append(d["speed"])
                voltage_record.append(d["voltage"])
        except JSONDecodeError:
            pass

    def on_disconnect(self, service: Service, connection: ConnectionBase) -> None:
        self.super(service=service, connection=connection)
        L.info("Disconnected")
        sleep(10)
        assert isinstance(service, Client)
        self.client = retry(service)


callback: CommCallback = CommCallback()

app: FastAPI = FastAPI(title="LEADS VeC Remote Analyst")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/")
async def index() -> str:
    return "LEADS VeC Remote Controller"


@app.get("/current")
async def current() -> dict[str, Any]:
    return data_record[-1] if len(data_record) > 0 else DataContainer().to_dict()


@app.get("/time_stamp")
async def time_stamp() -> list[int]:
    return time_stamp_record.to_list()


@app.get("/speed")
async def speed() -> list[float]:
    return speed_record.to_list()


@app.get("/time_lap")
async def time_lap() -> str:
    callback.client.send(b"time_lap")
    return "done"


@app.get("/hazard")
async def hazard() -> str:
    callback.client.send(b"hazard")
    return "done"


register(csv.close)
