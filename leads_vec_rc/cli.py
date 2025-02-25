from atexit import register
from datetime import datetime
from json import loads, JSONDecodeError
from os import makedirs
from os.path import abspath, exists
from time import sleep
from typing import Any, override

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from leads import require_config, L, DataContainer
from leads.comm import Service, Client, start_client, create_client, Callback, Connection, ConnectionBase
from leads.data_persistence import DataPersistence, CSV, DEFAULT_HEADER_FULL, VISUAL_HEADER_FULL
from leads_vec_rc.config import Config

config: Config = require_config()
if not exists(config.data_dir):
    L.debug(f"Data directory not found. Creating \"{abspath(config.data_dir)}\"...")
    makedirs(config.data_dir)
CAR_WIDTH: float = config.get("car_width", 2)
CAR_LENGTH: float = config.get("car_length", 1)
CAR_MASS: float = config.get("car_mass", 400)
CAR_CENTER_OF_MASS: float = config.get("car_center_of_mass", .25)

time_stamp_record: DataPersistence[int] = DataPersistence(2000)
csv: CSV | None = None


def try_create_csv(data: dict[str, Any]) -> None:
    global csv
    if csv:
        return
    csv = CSV(f"{config.data_dir}/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv",
              VISUAL_HEADER_FULL if set(VISUAL_HEADER_FULL).issubset(data.keys()) else DEFAULT_HEADER_FULL,
              time_stamp_record)
    register(csv.close)


def retry(service: Service) -> Client:
    L.warn("Retrying connection...")
    return start_client(config.comm_addr, create_client(service.port(), callback), True)


class CommCallback(Callback):
    def __init__(self) -> None:
        super().__init__()
        self.client: Client = start_client(config.comm_addr, create_client(config.comm_port, self), True)
        self.current_data: dict[str, Any] = DataContainer().to_dict()
        self.current_data.update({"report_rate": 0, "cfc_fl": 0, "cfc_fr": 0, "cfc_rl": 0, "cfc_rr": 0})

    @override
    def on_connect(self, service: Service, connection: Connection) -> None:
        self.super(service=service, connection=connection)
        L.info("Connected")

    @override
    def on_fail(self, service: Service, error: Exception) -> None:
        self.super(service=service, error=error)
        L.error(f"Comm client error: {repr(error)}")
        sleep(10)
        self.client = retry(service)

    @override
    def on_receive(self, service: Service, msg: bytes) -> None:
        self.super(service=service, msg=msg)
        try:
            d = loads(msg.decode())
            mg = CAR_MASS * 2.451675
            d["report_rate"] = 1000 * num_ts / (time_stamp_record[-1] - time_stamp_record[0]) if (num_ts := len(
                time_stamp_record)) > 1 else 0
            f_forward = CAR_MASS * d["forward_acceleration"] * CAR_CENTER_OF_MASS * .5 / CAR_WIDTH
            f_lateral = CAR_MASS * d["lateral_acceleration"] * CAR_CENTER_OF_MASS * .5 / CAR_LENGTH
            d["cfc_fl"] = mg + f_lateral - f_forward
            d["cfc_fr"] = mg - f_lateral - f_forward
            d["cfc_rl"] = mg + f_lateral + f_forward
            d["cfc_rr"] = mg - f_lateral + f_forward
            self.current_data = d
            if config.save_data:
                try_create_csv(d)
                csv.write_frame(*(d[key] for key in csv.header()))
            else:
                time_stamp_record.append(int(d["t"]))
        except JSONDecodeError:
            pass

    @override
    def on_disconnect(self, service: Service, connection: ConnectionBase) -> None:
        self.super(service=service, connection=connection)
        L.info("Disconnected")
        sleep(10)
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
    return callback.current_data


@app.get("/time_stamp")
async def time_stamp() -> list[int]:
    return time_stamp_record.to_list()


@app.get("/time_lap")
async def time_lap() -> str:
    callback.client.send(b"time_lap")
    return "done"


@app.get("/hazard")
async def hazard() -> str:
    callback.client.send(b"hazard")
    return "done"


@app.get("/m1")
async def m1() -> str:
    callback.client.send(b"m1")
    return "done"


@app.get("/m3")
async def m3() -> str:
    callback.client.send(b"m3")
    return "done"
