from atexit import register
from datetime import datetime
from json import loads, JSONDecodeError
from os import mkdir
from os.path import abspath, exists
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from leads import *
from leads.comm import *
from leads.data_persistence import *

config = require_config()
if not exists(config.data_dir):
    mkdir(config.data_dir)
    L.info(f"Data dir \"{abspath(config.data_dir)}\" created")

data_record: DataPersistence[DataContainer] = DataPersistence(1, compressor=lambda o, s: o[-s:])
time_stamp_record: DataPersistence[int] = DataPersistence(2000)
speed_record: DataPersistence[float] = DataPersistence(2000)
voltage_record: DataPersistence[float] = DataPersistence(2000)
gps_record: DataPersistence[Vector[float]] = DataPersistence(2000)
csv = CSVCollection(config.data_dir + "/" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ".csv", (
    "time_stamp", "speed", "voltage", "latitude", "longitude"
), time_stamp_record, speed_record, voltage_record, DataPersistence(1), DataPersistence(1))


class CommCallback(Callback):
    def on_connect(self, service: Service, connection: Connection) -> None:
        self.super(service=service, connection=connection)
        L.debug("Connected")

    def on_fail(self, service: Service, error: Exception) -> None:
        self.super(service=service, error=error)
        L.error("Comm client error: " + repr(error))

    def on_receive(self, service: Service, msg: bytes) -> None:
        self.super(service=service, msg=msg)
        try:
            d = loads(msg.decode())
            data_record.append(d)
            ts, fws, vot, lat, lon = d["t"], d["front_wheel_speed"], d["voltage"], d["latitude"], d["longitude"]
            gps_record.append(Vector(lat, lon))
            if config.enable_data_persistence:
                csv.write_frame(ts, fws, vot, lat, lon)
            else:
                time_stamp_record.append(ts)
                speed_record.append(fws)
                voltage_record.append(vot)
        except JSONDecodeError as e:
            L.error(repr(e))


client = start_client(config.comm_addr, create_client(config.comm_port, CommCallback()), True)

app = FastAPI(title="LEADS VeC Remote Controller")

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
    return data_record[-1] if len(data_record) > 0 else SRWDataContainer(
    ).to_dict() if config.srw_mode else DRWDataContainer(
    ).to_dict()


@app.get("/time_stamp")
async def time_stamp() -> list[int]:
    return time_stamp_record.to_list()


@app.get("/speed")
async def speed() -> list[float]:
    return speed_record.to_list()


@app.get("/time_lap")
async def time_lap() -> str:
    client.send(b"time_lap")
    return "done"


@app.get("/hazard")
async def hazard() -> str:
    client.send(b"hazard")
    return "done"


@register
def cleanup() -> None:
    csv.close()
