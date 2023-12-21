from datetime import datetime
from time import time
from tkinter import Button, Label

from keyboard import add_hotkey

from leads import *
from leads.comm import *
from leads_dashboard import *
from leads_vec.__version__ import __version__
from leads_vec.config import Config


class CustomRuntimeData(RuntimeData):
    m1_mode: int = 0
    m3_mode: int = 0


def main(main_controller: Controller, config: Config) -> int:
    context = Leads(srw_mode=config.srw_mode)

    def render(manager: ContextManager):
        def switch_m1_mode():
            manager.rd().m1_mode = (manager.rd().m1_mode + 1) % 2

        def switch_m3_mode():
            manager.rd().m3_mode = (manager.rd().m3_mode + 1) % 3

        manager["m1"] = Button(manager.root(),
                               font=H1,
                               command=switch_m1_mode,
                               width=int(manager.window().width() * .33 / H1[1]),
                               height=7)
        manager["m1"].grid(row=0, column=0, rowspan=2, columnspan=20, sticky="NSEW")
        manager["m2"] = Button(manager.root(),
                               font=H1,
                               width=int(manager.window().width() * .33 / H1[1]),
                               height=7)
        manager["m2"].grid(row=0, column=20, rowspan=2, columnspan=20, sticky="NSEW")
        manager["m3"] = Button(manager.root(),
                               font=H1,
                               command=switch_m3_mode,
                               width=int(manager.window().width() * .33 / H1[1]),
                               height=7)
        manager["m3"].grid(row=0, column=40, rowspan=2, columnspan=20, sticky="NSEW")
        manager["dtcs_status"] = Label(manager.root(), text="DTCS READY", foreground="green")
        manager["dtcs_status"].grid(row=3, column=0, columnspan=12)
        manager["abs_status"] = Label(manager.root(), text="ABS READY", foreground="green")
        manager["abs_status"].grid(row=3, column=12, columnspan=12)
        manager["ebi_status"] = Label(manager.root(), text="EBI READY", foreground="green")
        manager["ebi_status"].grid(row=3, column=24, columnspan=12)
        manager["atbs_status"] = Label(manager.root(), text="ATBS READY", foreground="green")
        manager["atbs_status"].grid(row=3, column=36, columnspan=12)
        manager["comm_status"] = Label(manager.root(), text="COMM ONLINE", foreground="white")
        manager["comm_status"].grid(row=3, column=48, columnspan=12)

        def switch_dtcs():
            context.set_dtcs(not (dtcs_enabled := context.is_dtcs_enabled()))
            manager["dtcs"].config(text=f"DTCS {'OFF' if dtcs_enabled else 'ON'}")

        add_hotkey("1", switch_dtcs)

        def switch_abs():
            context.set_abs(not (abs_enabled := context.is_abs_enabled()))
            manager["abs"].config(text=f"ABS {'OFF' if abs_enabled else 'ON'}")

        add_hotkey("2", switch_abs)

        def switch_ebi():
            context.set_ebi(not (ebi_enabled := context.is_ebi_enabled()))
            manager["ebi"].config(text=f"EBI {'OFF' if ebi_enabled else 'ON'}")

        add_hotkey("3", switch_ebi)

        def switch_atbs():
            context.set_atbs(not (atbs_enabled := context.is_atbs_enabled()))
            manager["atbs"].config(text=f"ATBS {'OFF' if atbs_enabled else 'ON'}")

        add_hotkey("4", switch_atbs)

        manager["dtcs"] = Button(manager.root(), text="DTCS ON", command=switch_dtcs)
        manager["dtcs"].grid(row=4, column=0, columnspan=15)
        manager["abs"] = Button(manager.root(), text="ABS ON", command=switch_abs)
        manager["abs"].grid(row=4, column=15, columnspan=15)
        manager["ebi"] = Button(manager.root(), text="EBI ON", command=switch_ebi)
        manager["ebi"].grid(row=4, column=30, columnspan=15)
        manager["atbs"] = Button(manager.root(), text="ATBS ON", command=switch_atbs)
        manager["atbs"].grid(row=4, column=45, columnspan=15)

    uim = initialize(Window(1920, 1080, config.refresh_rate, CustomRuntimeData()), render, context, main_controller)

    class CustomCallback(Callback):
        def on_fail(self, service: Service, error: Exception) -> None:
            uim.rd().comm = None
            uim["comm_status"].config(text="COMM OFFLINE", foreground="gray")

        def on_receive(self, service: Service, msg: bytes) -> None:
            print(msg)

    uim.rd().comm = start_client(config.comm_addr, create_client(config.comm_port, CustomCallback()), True)

    class CustomListener(EventListener):
        def on_push(self, e: DataPushedEvent) -> None:
            try:
                uim.rd().comm_notify(e.data)
            except IOError:
                uim.rd().comm_kill()
                uim.rd().comm = None
                uim["comm_status"].config(text="COMM OFFLINE", foreground="gray")

        def on_update(self, e: UpdateEvent) -> None:
            duration = int(time()) - uim.rd().start_time
            if uim.rd().m1_mode == 0:
                uim["m1"].config(font=H5, text="LAP TIME\n\nLAP1 9s\nLAP2 11s\nLAP3 10s")
            elif uim.rd().m1_mode == 1:
                uim["m1"].config(font=BODY, text=f"VeC {__version__.upper()}\n\n"
                                                 f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                                                 f"{duration // 60} MIN {duration % 60} SEC\n\n"
                                                 f"{'SRW MODE' if config.srw_mode else 'DRW MODE'}\n"
                                                 f"REFRESH RATE: {config.refresh_rate} FPS")
            uim["m2"].config(text=f"{int(context.data().front_wheel_speed)}")
            if uim.rd().m3_mode == 0:
                uim["m3"].config(font=H1, text="0.0V")
            elif uim.rd().m3_mode == 1:
                uim["m3"].config(font=H5, text="G Force")
            else:
                uim["m3"].config(font=H5, text="Speed Trend")

        def on_intervene(self, e: InterventionEvent) -> None:
            uim[e.system.lower() + "_status"].config(text=e.system + " INTERVENED", foreground="purple")

        def post_intervene(self, e: InterventionEvent) -> None:
            uim[e.system.lower() + "_status"].config(text=e.system + " READY", foreground="green")

        def on_suspend(self, e: SuspensionEvent) -> None:
            uim[e.system.lower() + "_status"].config(text=e.system + " SUSPENDED", foreground="red")

        def post_suspend(self, e: SuspensionEvent) -> None:
            uim[e.system.lower() + "_status"].config(text=e.system + " READY", foreground="green")

    context.set_event_listener(CustomListener())
    uim.show()
    uim.rd().comm_kill()
    return 0
