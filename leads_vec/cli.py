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
        ctx.plugin(system).enabled = not ctx.plugin(system).enabled
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

        manager["record_lap"] = CTkButton(manager.root(), text="Record Lap", command=ctx.record_lap,
                                          font=("Arial", cfg.font_size_small))

        def switch_ecs_mode(mode):
            manager["ecs"].configure(selected_color=(c := "green" if ECSMode[mode] < 2 else "red"),
                                     selected_hover_color=c)

        manager["ecs"] = CTkSegmentedButton(manager.root(), values=["STANDARD", "AGGRESSIVE", "SPORT"],
                                            variable=ecs, command=switch_ecs_mode, font=("Arial", cfg.font_size_small))

    uim = initialize(window, render, ctx, get_controller(MAIN_CONTROLLER))

    class CommCallback(Callback):
        def on_fail(self, service: Service, error: Exception) -> None:
            L.error("Comm server error: " + str(error))

        def on_connect(self, service: Service, connection: Connection) -> None:
            uim["comm_status"].configure(text="COMM ONLINE", text_color="black")

    uim.rd().comm = start_server(create_server(cfg.comm_port, CommCallback()), True)

    def format_lap_time(t: int) -> str:
        return f"{(t := int(t * .001)) // 60} MIN {t % 60} SEC"

    class CustomListener(EventListener):
        def on_push(self, e: DataPushedEvent) -> None:
            uim.rd().comm_notify(e.data)

        def post_update(self, e: UpdateEvent) -> None:
            d = ctx.data()
            if uim.rd().m1_mode == 0:
                m1.set("LAP TIME\n\n" + "\n".join(map(format_lap_time, ctx.get_lap_time_list())))
            else:
                m1.set(f"VeC {__version__.upper()}\n\n"
                       f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n"
                       f"{(duration := int(time()) - uim.rd().start_time) // 60} MIN {duration % 60} SEC\n\n"
                       f"{"SRW MODE" if cfg.srw_mode else "DRW MODE"}\n"
                       f"REFRESH RATE: {cfg.refresh_rate} FPS")
            m2.set(int(d.speed))
            if uim.rd().m3_mode == 0:
                m3.set("0.0V")
            elif uim.rd().m3_mode == 1:
                m3.set("G Force")
            else:
                m3.set(f"Speed Trend\n"
                       f"{(sts := str(st := ctx.get_speed_trend() * 10))[:sts.find(".") + 2]} {"↑" if st > 0 else "↓"}")
            if uim.rd().comm.num_connections() < 1:
                uim["comm_status"].configure(text="COMM OFFLINE", text_color="gray")
            if uim.rd().control_system_switch_changed:
                for system in SystemLiteral:
                    system_lowercase = system.lower()
                    if ctx.plugin(SystemLiteral(system)).enabled:
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
    uim["battery_failure"] = CTkLabel(uim.root(), text="")
    uim["ecs_failure"] = CTkLabel(uim.root(), text="")
    uim["motor_failure"] = CTkLabel(uim.root(), text="")
    uim["wheel_speed_failure"] = CTkLabel(uim.root(), text="")

    def on_fail(_, e: SuspensionEvent) -> None:
        if e.system == "ECS":
            uim["ecs_failure"].configure(image=ECS(color=Color.RED))
        elif e.system == "WSC":
            uim["wheel_speed_failure"].configure(image=Speed(color=Color.RED))

    SFT.on_fail = on_fail

    def on_recover(_, e: SuspensionEvent) -> None:
        if e.system == "ECS":
            uim["ecs_failure"].configure(image=None)
        if e.system == "WSC":
            uim["wheel_speed_failure"].configure(image=None)

    SFT.on_recover = on_recover
    layout = [
        ["m1", "m2", "m3"],
        ["dtcs_status", "abs_status", "ebi_status", "atbs_status", "comm_status"],
        list(map(lambda s: s.lower(), SystemLiteral)),
        ["record_lap", "ecs"],
        ["battery_failure", "ecs_failure", "motor_failure", "wheel_speed_failure"]
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
