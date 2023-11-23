from datetime import datetime
from time import time

from dearpygui import dearpygui as dpg
from keyboard import add_hotkey

from leads import *
from leads.comm import *
from leads_dashboard import *
from .__version__ import __version__


class CustomRuntimeData(RuntimeData):
    m1_mode: int = 0
    m3_mode: int = 0


def main(main_controller: Controller,
         srw_mode: bool = True,
         analysis_rate: float = .01,
         update_rate: float = .25,
         communication_server_address: str = "") -> int:
    context = Leads(srw_mode=srw_mode)
    rd = CustomRuntimeData()

    class CustomCallback(Callback):
        def on_fail(self, service: Service, error: Exception):
            rd.comm = None

        def on_receive(self, service: Service, msg: bytes):
            print(msg)

    if communication_server_address != "":
        rd.comm = start_client(communication_server_address,
                               create_client(callback=CustomCallback()),
                               True)

    def switch_m1_mode():
        rd.m1_mode = (rd.m1_mode + 1) % 2

    def switch_m3_mode():
        rd.m3_mode = (rd.m3_mode + 1) % 3

    def switch_dtcs():
        context.set_dtcs(not (dtcs_enabled := context.is_dtcs_enabled()))
        dpg.set_item_label("dtcs", f"DTCS {'OFF' if dtcs_enabled else 'ON'}")

    add_hotkey("1", switch_dtcs)

    def switch_abs():
        context.set_abs(not (abs_enabled := context.is_abs_enabled()))
        dpg.set_item_label("abs", f"ABS {'OFF' if abs_enabled else 'ON'}")

    add_hotkey("2", switch_abs)

    def switch_ebi():
        context.set_ebi(not (ebi_enabled := context.is_ebi_enabled()))
        dpg.set_item_label("ebi", f"EBI {'OFF' if ebi_enabled else 'ON'}")

    add_hotkey("3", switch_ebi)

    def switch_atbs():
        context.set_atbs(not (atbs_enabled := context.is_atbs_enabled()))
        dpg.set_item_label("atbs", f"ATBS {'OFF' if atbs_enabled else 'ON'}")

    add_hotkey("4", switch_atbs)

    def render():
        with dpg.table(header_row=False):
            dpg.add_table_column()
            dpg.add_table_column()
            dpg.add_table_column()
            with dpg.table_row():
                dpg.bind_item_font(dpg.add_button(label="", tag="m1", width=-1, height=140), BODY2)
                dpg.set_item_callback("m1", switch_m1_mode)
                dpg.bind_item_font(dpg.add_button(label="0", tag="m2", width=-1, height=140), H1)
                dpg.bind_item_font(dpg.add_button(label="0.0v", tag="m3", width=-1, height=140), H1)
                dpg.set_item_callback("m3", switch_m3_mode)
        with dpg.table(header_row=False):
            dpg.add_table_column()
            dpg.add_table_column()
            dpg.add_table_column()
            dpg.add_table_column()
            dpg.add_table_column()
            with dpg.table_row():
                dpg.bind_item_font(dpg.add_text("DTCS READY", color=(0, 255, 0), tag="dtcs_status"), BODY)
                dpg.bind_item_font(dpg.add_text("ABS READY", color=(0, 255, 0), tag="abs_status"), BODY)
                dpg.bind_item_font(dpg.add_text("EBI READY", color=(0, 255, 0), tag="ebi_status"), BODY)
                dpg.bind_item_font(dpg.add_text("ATBS READY", color=(0, 255, 0), tag="atbs_status"), BODY)
                dpg.bind_item_font(dpg.add_text("COMM ONLINE", tag="comm_status"), BODY)
            with dpg.table_row():
                dpg.bind_item_font(dpg.add_button(label="DTCS ON",
                                                  tag="dtcs",
                                                  width=-1,
                                                  callback=switch_dtcs), BODY)
                dpg.bind_item_font(dpg.add_button(label="ABS ON",
                                                  tag="abs",
                                                  width=-1,
                                                  callback=switch_abs), BODY)
                dpg.bind_item_font(dpg.add_button(label="EBI ON",
                                                  tag="ebi",
                                                  width=-1,
                                                  callback=switch_ebi), BODY)
                dpg.bind_item_font(dpg.add_button(label="ATBS ON",
                                                  tag="atbs",
                                                  width=-1,
                                                  callback=switch_atbs), BODY)

    class CustomListener(EventListener):
        def on_push(self, e: DataPushedEvent):
            rd.comm_notify(e.data)

        def on_update(self, e: UpdateEvent):
            duration = int(time()) - rd.start_time
            if rd.m1_mode == 0:
                dpg.set_item_label("m1", "LAP TIME\n\nLAP1 9s\nLAP2 11s\nLAP3 10s")
            elif rd.m1_mode == 1:
                dpg.set_item_label("m1",
                                   f"VeC {__version__.upper()}\n\n"
                                   f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                                   f"{duration // 60} MIN {duration % 60} SEC\n\n"
                                   f"{'SRW MODE' if srw_mode else 'DRW MODE'}\n"
                                   f"ANALYSIS RATE: {int(1 / analysis_rate)} TPS\n"
                                   f"UPDATE RATE: {int(1 / update_rate)} TPS")
            dpg.set_item_label("m2", f"{context.data().front_wheel_speed}")
            if rd.m3_mode == 0:
                dpg.bind_item_font("m3", H1)
                dpg.set_item_label("m3", "0.0v")
            elif rd.m3_mode == 1:
                dpg.bind_item_font("m3", BODY)
                dpg.set_item_label("m3", "G Force")
            else:
                dpg.bind_item_font("m3", BODY)
                dpg.set_item_label("m3", "SPEED TREND")
            dpg.set_value("comm_status", "COMM ONLINE" if rd.comm else "COMM OFFLINE")

        def on_intervene(self, e: InterventionEvent):
            dpg.set_value(e.system + "_status", e.system + " INTERVENED")

        def post_intervene(self, e: InterventionEvent):
            dpg.set_value(e.system + "_status", e.system + " READY")

        def on_suspend(self, e: SuspensionEvent):
            dpg.set_value(e.system + "_status", e.system + " SUSPENDED")

        def post_suspend(self, e: SuspensionEvent):
            dpg.set_value(e.system + "_status", e.system + " READY")

    context.set_event_listener(CustomListener())
    start(render, context, main_controller, analysis_rate, update_rate, rd)
    rd.comm_kill()
    return 0
