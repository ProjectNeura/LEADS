from datetime import datetime
from time import time
from typing import Callable

from customtkinter import CTkButton, CTkLabel, IntVar, StringVar, CTkSegmentedButton
from keyboard import add_hotkey

from leads import *
from leads.comm import *
from leads_gui import *
from leads_vec.__version__ import __version__


class CustomRuntimeData(RuntimeData):
    m1_mode: int = 0
    m3_mode: int = 0
    control_system_switch_changed: bool = False


def make_system_switch(ctx: LEADS, system: SystemLiteral, runtime_data: RuntimeData) -> Callable[[], None]:
    def switch() -> None:
        ctx.plugin(system).enabled(not ctx.plugin(system).enabled())
        runtime_data.control_system_switch_changed = True

    return switch


def main() -> int:
    cfg = get_config(Config)
    ctx = LEADS[SRWDataContainer if cfg.srw_mode else DRWDataContainer](srw_mode=cfg.srw_mode)
    ctx.plugin(SystemLiteral.DTCS, DTCS())
    ctx.plugin(SystemLiteral.ABS, ABS())
    ctx.plugin(SystemLiteral.EBI, EBI())
    ctx.plugin(SystemLiteral.ATBS, ATBS())
    SFT.bind_context(ctx)
    window = Window(cfg.width,
                    cfg.height,
                    cfg.refresh_rate,
                    CustomRuntimeData(),
                    fullscreen=cfg.fullscreen,
                    no_title_bar=cfg.no_title_bar)
    m1 = StringVar(window.root(), "")
    m2 = IntVar(window.root(), 0)
    m3 = StringVar(window.root(), "")
    ecs = StringVar(window.root(), "STANDARD")

    def render(manager: ContextManager):
        def switch_m1_mode():
            manager.rd().m1_mode = (manager.rd().m1_mode + 1) % 2

        def switch_m3_mode():
            manager.rd().m3_mode = (manager.rd().m3_mode + 1) % 3

        manager["m1"] = CTkButton(manager.root(), textvariable=m1, command=switch_m1_mode,
                                  font=("Arial", cfg.font_size_small))
        manager["m2"] = CTkButton(manager.root(), textvariable=m2, state="disabled",
                                  font=("Arial", cfg.font_size_x_large))
        manager["m3"] = CTkButton(manager.root(), textvariable=m3, command=switch_m3_mode,
                                  font=("Arial", cfg.font_size_medium))

        manager["comm_status"] = CTkLabel(manager.root(), text="COMM OFFLINE", text_color="gray",
                                          font=("Arial", cfg.font_size_small))

        i = 0
        for system in SystemLiteral:
            i += 1
            system_lower = system.lower()
            manager[system_lower + "_status"] = CTkLabel(manager.root(), text=system + " READY", text_color="green",
                                                         font=("Arial", cfg.font_size_small))
            add_hotkey(str(i), switch := make_system_switch(ctx, SystemLiteral(system), manager.rd()))
            manager[system_lower] = CTkButton(manager.root(), text=system + " ON", command=switch,
                                              font=("Arial", cfg.font_size_small))

        manager["time_lap"] = CTkButton(manager.root(), text="Time Lap", command=ctx.time_lap,
                                        font=("Arial", cfg.font_size_small))

        def hazard():
            ctx.hazard(not ctx.hazard())
            manager["hazard"].configure(image=Hazard(color=Color.RED if ctx.hazard() else None))

        manager["hazard"] = CTkButton(manager.root(), text="", image=Hazard(), command=hazard)

        def switch_ecs_mode(mode):
            manager["ecs"].configure(selected_color=(c := "green" if (ecs_mode := ECSMode[mode]) < 2 else "red"),
                                     selected_hover_color=c)
            ctx.ecs_mode(ecs_mode)
            manager.rd().control_system_switch_changed = True

        manager["ecs"] = CTkSegmentedButton(manager.root(), values=["STANDARD", "AGGRESSIVE", "SPORT", "OFF"],
                                            variable=ecs, command=switch_ecs_mode, font=("Arial", cfg.font_size_small))

    uim = initialize(window, render, ctx, get_controller(MAIN_CONTROLLER))

    class CommCallback(Callback):
        def on_fail(self, service: Service, error: Exception) -> None:
            L.error("Comm server error: " + repr(error))

        def on_receive(self, service: Service, msg: bytes) -> None:
            if msg == b"time_lap":
                ctx.time_lap()

    uim.rd().comm = start_server(create_server(cfg.comm_port, CommCallback()), True)

    def format_lap_time(t: int) -> str:
        return f"{(t := int(t * .001)) // 60} MIN {t % 60} SEC"

    class CustomListener(EventListener):
        def on_push(self, e: DataPushedEvent) -> None:
            d = e.data.to_dict()
            d["speed_trend"] = ctx.get_speed_trend()
            d["lap_times"] = ctx.get_lap_time_list()
            uim.rd().comm_notify(d)

        def post_update(self, e: UpdateEvent) -> None:
            d = e.context.data()
            if uim.rd().m1_mode == 0:
                lap_time_list = ctx.get_lap_time_list()
                m1.set("LAP TIMES\n\n" + ("No Lap Timed" if len(lap_time_list) < 1 else "\n".join(map(format_lap_time,
                                                                                                      lap_time_list))))
            else:
                m1.set(f"VeC {__version__.upper()}\n\n"
                       f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n"
                       f"{(duration := int(time()) - uim.rd().start_time) // 60} MIN {duration % 60} SEC\n"
                       f"{(m := d.mileage):.1f} KM - {m * 3600 / duration:.1f} KM / H\n\n"
                       f"{"SRW MODE" if cfg.srw_mode else "DRW MODE"}\n"
                       f"{cfg.refresh_rate} FPS\n"
                       f"{ip[-1] if len(ip := my_ip_addresses()) > 0 else "NOT FOUND"}:{uim.rd().comm.port()}")
            m2.set(int(d.speed))
            if uim.rd().m3_mode == 0:
                m3.set(f"{d.voltage:.1f} V")
            elif uim.rd().m3_mode == 1:
                m3.set("G Force")
            else:
                m3.set(f"Speed Trend\n"
                       f"{(st := ctx.get_speed_trend() * 10):.1f} {"↑" if st > 0 else "↓"}")
            if uim.rd().comm.num_connections() < 1:
                uim["comm_status"].configure(text="COMM OFFLINE", text_color="gray")
            else:
                uim["comm_status"].configure(text="COMM ONLINE", text_color=["black", "white"])
            if uim.rd().control_system_switch_changed:
                for system in SystemLiteral:
                    system_lowercase = system.lower()
                    if ctx.plugin(SystemLiteral(system)).enabled():
                        uim[system_lowercase].configure(text=system + " ON")
                    else:
                        uim[system_lowercase].configure(text=system + " OFF")
                        uim[system_lowercase + "_status"].configure(text=system + " OFF", text_color=("black", "white"))
                uim.rd().control_system_switch_changed = False

        def on_intervene(self, e: InterventionEvent) -> None:
            if e.system in SystemLiteral:
                uim[e.system.lower() + "_status"].configure(text=e.system + " INTEV", text_color="red")

        def post_intervene(self, e: InterventionEvent) -> None:
            if e.system in SystemLiteral:
                uim[e.system.lower() + "_status"].configure(text=e.system + " READY", text_color="green")

        def on_suspend(self, e: SuspensionEvent) -> None:
            if e.system in SystemLiteral:
                uim[e.system.lower() + "_status"].configure(text=e.system + " SUSPD", text_color="gray")

        def post_suspend(self, e: SuspensionEvent) -> None:
            if e.system in SystemLiteral:
                uim[e.system.lower() + "_status"].configure(text=e.system + " READY", text_color="green")

    ctx.set_event_listener(CustomListener())
    uim["battery_fault"] = CTkLabel(uim.root(), text="")
    uim["ecs_fault"] = CTkLabel(uim.root(), text="")
    uim["gps_fault"] = CTkLabel(uim.root(), text="")
    uim["motor_fault"] = CTkLabel(uim.root(), text="")
    uim["wheel_speed_fault"] = CTkLabel(uim.root(), text="")

    def on_fail(_, e: SuspensionEvent) -> None:
        if e.system == "ECS":
            uim["ecs_fault"].configure(image=ECS(color=Color.RED))
        elif e.system == "BATT":
            uim["battery_fault"].configure(image=Battery(color=Color.RED))
        elif e.system == "MOTOR":
            uim["motor_fault"].configure(image=Motor(color=Color.RED))
        elif e.system == "WSC":
            uim["wheel_speed_fault"].configure(image=Speed(color=Color.RED))
        elif e.system == "GPS":
            uim["gps_fault"].configure(image=Satellite(color=Color.RED))

    SFT.on_fail = on_fail

    def on_recover(_, e: SuspensionEvent) -> None:
        if e.system == "ECS":
            uim["ecs_fault"].configure(image=None)
        elif e.system == "BATT":
            uim["battery_fault"].configure(image=None)
        elif e.system == "MOTOR":
            uim["motor_fault"].configure(image=None)
        elif e.system == "WSC":
            uim["wheel_speed_fault"].configure(image=None)
        elif e.system == "GPS":
            uim["gps_fault"].configure(image=None)

    SFT.on_recover = on_recover
    layout = [
        ["m1", "m2", "m3"],
        ["dtcs_status", "abs_status", "ebi_status", "atbs_status", "comm_status"],
        list(map(lambda s: s.lower(), SystemLiteral)),
        ["ecs"],
        ["time_lap", "hazard"],
        ["battery_fault", "ecs_fault", "gps_fault", "motor_fault", "wheel_speed_fault"]
    ]
    uim.layout(layout)
    placeholder_row = len(layout)
    CTkLabel(uim.root(), text="").grid(row=placeholder_row, column=0)
    uim.root().grid_rowconfigure(0, weight=1)
    uim.root().grid_rowconfigure(placeholder_row, weight=2)
    initialize_main()
    uim.show()
    uim.rd().comm_kill()
    return 0
