from json import loads
from os.path import abspath as _abspath

from fastapi import FastAPI

from leads.comm import *
from leads.utils import *
from leads_dashboard import *

config = load_config("")
time_stamp_record = DataPersistence(_abspath(__file__)[:-6] + "config.json", max_size=2000)
speed_record = DataPersistence(_abspath(__file__)[:-6] + "config.json", max_size=2000)


class CustomCallback(Callback):
    def on_receive(self, service: Service, msg: bytes) -> None:
        data = loads(msg.decode())
        time_stamp_record.append(data["t"])
        speed_record.append(data["front_wheel_speed"])

    def on_disconnect(self, service: Service, connection: Connection) -> None:
        time_stamp_record.close()
        speed_record.close()


client = start_client("127.0.0.1", create_client(), True)

app = FastAPI(title="LEADS VeC Remote Controller")


@app.get("/")
async def index():
    return {"message": "Hello World"}
