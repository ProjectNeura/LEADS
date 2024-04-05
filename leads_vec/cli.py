from datetime import datetime
from time import time
from typing import Callable

from customtkinter import CTkButton, CTkLabel, DoubleVar, StringVar, CTkSegmentedButton
from keyboard import add_hotkey

from leads import *
from leads.comm import *
from leads_gui import *
from leads_vec.__version__ import __version__


class CustomRuntimeData(RuntimeData):
    m1_mode: int = 0
    control_system_switch_changed: bool = False


def make_system_switch(ctx: LEADS, system: SystemLiteral, runtime_data: RuntimeData) -> Callable[[], None]:
    def switch() -> None:
        ctx.plugin(system).enabled(not ctx.plugin(system).enabled())
        runtime_data.control_system_switch_changed = True

    return switch


def main() -> int:
    cfg = require_config()
    ctx = LEADS(srw_mode=cfg.srw_mode, data_seq_size=cfg.data_seq_size)
    register_context(ctx)
    ctx.plugin(SystemLiteral.DTCS, DTCS())
    ctx.plugin(SystemLiteral.ABS, ABS())
    ctx.plugin(SystemLiteral.EBI, EBI())
    ctx.plugin(SystemLiteral.ATBS, ATBS())
    ctx.plugin("GPS_SPEED_CORRECTION", GPSSpeedCorrection())
    window = Window(cfg.width,
                    cfg.height,
                    cfg.refresh_rate,
                    CustomRuntimeData(),
                    fullscreen=cfg.fullscreen,
                    no_title_bar=cfg.no_title_bar)
    root = window.root()
    root.configure(cursor="dot")
    m1 = StringVar(root, "")
    speed = DoubleVar(root, 0)
    voltage = StringVar(root, "")
    speed_trend = DoubleVar(root, 0)
    g_force = GForceVar(root, 0, 0)
    esc = StringVar(root, "STANDARD")

    def render(manager: ContextManager):
        def switch_m1_mode(_):
            manager.rd().m1_mode = (manager.rd().m1_mode + 1) % 3

        manager["m1"] = Typography(root, theme_key="CTkButton", variable=m1, clickable=True,
                                   command=switch_m1_mode, font=("Arial", cfg.font_size_small - 4)).lock_ratio(.7)
        manager["m2"] = Speedometer(root, variable=speed).lock_ratio(.7)
        manager["m3"] = ProxyCanvas(root, "CTkButton",
                                    Typography(root, theme_key="CTkButton", variable=voltage,
                                               font=("Arial", cfg.font_size_medium - 4)),
                                    SpeedTrendMeter(root, theme_key="CTkButton", variable=speed_trend,
                                                    font=("Arial", cfg.font_size_medium - 4)),
                                    GForceMeter(root, theme_key="CTkButton", variable=g_force,
                                                font=("Arial", cfg.font_size_medium - 4))).lock_ratio(.7)

        manager["comm_status"] = CTkLabel(root, text="COMM OFFLINE", text_color="gray",
                                          font=("Arial", cfg.font_size_small))

        i = 0
        for system in SystemLiteral:
            i += 1
            system_lower = system.lower()
            manager[system_lower + "_status"] = CTkLabel(root, text=system + " READY", text_color="green",
                                                         font=("Arial", cfg.font_size_small))
            add_hotkey(str(i), switch := make_system_switch(ctx, SystemLiteral(system), manager.rd()))
            manager[system_lower] = CTkButton(root, text=system + " ON", command=switch,
                                              font=("Arial", cfg.font_size_small))

        manager["time_lap"] = CTkButton(root, text="Time Lap", command=ctx.time_lap,
                                        font=("Arial", cfg.font_size_small))

        def hazard():
            ctx.hazard(not ctx.hazard())
            manager["hazard"].configure(image=Hazard(color=Color.RED if ctx.hazard() else None))

        manager["hazard"] = CTkButton(root, text="", image=Hazard(), command=hazard)

        def switch_esc_mode(mode):
            manager["esc"].configure(selected_color=(c := "green" if (esc_mode := ESCMode[mode]) < 2 else "red"),
                                     selected_hover_color=c)
            ctx.esc_mode(esc_mode)
            manager.rd().control_system_switch_changed = True

        manager["esc"] = CTkSegmentedButton(root, values=["STANDARD", "AGGRESSIVE", "SPORT", "OFF"], variable=esc,
                                            command=switch_esc_mode, font=("Arial", cfg.font_size_small))

    uim = initialize(window, render, ctx, get_controller(MAIN_CONTROLLER))

    class CommCallback(Callback):
        def on_fail(self, service: Service, error: Exception) -> None:
            self.super(service=service, error=error)
            L.error("Comm server error: " + repr(error))

        def on_receive(self, service: Service, msg: bytes) -> None:
            self.super(service=service, msg=msg)
            if msg == b"time_lap":
                ctx.time_lap()

    uim.rd().comm = start_server(create_server(cfg.comm_port, CommCallback()), True)

    def format_lap_time(t: int) -> str:
        return f"{(t := int(t * .001)) // 60} MIN {t % 60} SEC"

    class CustomListener(EventListener):
        def pre_push(self, e: DataPushedEvent) -> None:
            self.super(e)
            d = e.data.to_dict()
            d["speed_trend"] = ctx.get_speed_trend()
            d["lap_times"] = ctx.get_lap_time_list()
            uim.rd().comm_notify(d)

        def on_update(self, e: UpdateEvent) -> None:
            self.super(e)
            d = e.context.data()
            if uim.rd().m1_mode == 0:
                lap_time_list = ctx.get_lap_time_list()
                m1.set("LAP TIMES\n\n" + ("No Lap Timed" if len(lap_time_list) < 1 else "\n".join(map(format_lap_time,
                                                                                                      lap_time_list))))
            elif uim.rd().m1_mode == 1:
                gps = get_device(GPS_RECEIVER).read()
                m1.set(f"GPS {"VALID" if d.gps_valid else "NO FIX"} - {gps[4]} {gps[5]}\n\n"
                       f"{d.gps_ground_speed:.1f} KM / H\n"
                       f"LAT {d.latitude:.5f}\nLON {d.longitude:.5f}")
            elif uim.rd().m1_mode == 2:
                m1.set(f"VeC {__version__.upper()}\n\n"
                       f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n"
                       f"{(duration := int(time()) - uim.rd().start_time) // 60} MIN {duration % 60} SEC\n"
                       f"{(m := d.mileage):.1f} KM - {m * 3600 / duration:.1f} KM / H\n\n"
                       f"{"SRW MODE" if cfg.srw_mode else "DRW MODE"}\n"
                       f"{cfg.refresh_rate} - {uim.fps():.2f} FPS\n"
                       f"{ip[-1] if len(ip := my_ip_addresses()) > 0 else "NOT FOUND"}:{uim.rd().comm.port()}")
            speed.set(d.speed)
            voltage.set(f"{d.voltage:.1f} V")
            st = ctx.get_speed_trend()
            speed_trend.set(st)
            g_force.set((d.lateral_acceleration, d.forward_acceleration))
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

        def pre_intervene(self, e: InterventionEvent) -> None:
            self.super(e)
            if e.system in SystemLiteral:
                uim[e.system.lower() + "_status"].configure(text=e.system + " INTEV", text_color="red")

        def post_intervene(self, e: InterventionEvent) -> None:
            self.super(e)
            if e.system in SystemLiteral:
                uim[e.system.lower() + "_status"].configure(text=e.system + " READY", text_color="green")

        def pre_suspend(self, e: SuspensionEvent) -> None:
            self.super(e)
            if e.system in SystemLiteral:
                uim[e.system.lower() + "_status"].configure(text=e.system + " SUSPD", text_color="gray")

        def post_suspend(self, e: SuspensionEvent) -> None:
            self.super(e)
            if e.system in SystemLiteral:
                uim[e.system.lower() + "_status"].configure(text=e.system + " READY", text_color="green")

    ctx.set_event_listener(CustomListener())
    uim["battery_fault"] = CTkLabel(root, text="")
    uim["esc_fault"] = CTkLabel(root, text="")
    uim["gps_fault"] = CTkLabel(root, text="")
    uim["motor_fault"] = CTkLabel(root, text="")
    uim["wheel_speed_fault"] = CTkLabel(root, text="")

    def on_fail(_, e: SuspensionEvent) -> None:
        if e.system == "ESC":
            uim["esc_fault"].configure(image=ESC(color=Color.RED))
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
        if e.system == "ESC":
            uim["esc_fault"].configure(image=None)
        elif e.system == "BATT":
            uim["battery_fault"].configure(image=None)
        elif e.system == "MOTOR":
            uim["motor_fault"].configure(image=None)
        elif e.system == "WSC":
            uim["wheel_speed_fault"].configure(image=None)
        elif e.system == "GPS":
            uim["gps_fault"].configure(image=None)

    SFT.on_recover = on_recover
    if cfg.manual_mode:
        layout = [
            ["m1", "m2", "m3"],
            [CTkLabel(root, text="MANUAL MODE"), CTkLabel(root, text="ASSISTANCE DISABLED"), "comm_status"],
            ["time_lap", "hazard"],
            ["battery_fault", "esc_fault", "gps_fault", "motor_fault", "wheel_speed_fault"]
        ]
        ctx.esc_mode(ESCMode.OFF)
        uim.rd().control_system_switch_changed = True
    else:
        layout = [
            ["m1", "m2", "m3"],
            [*map(lambda s: s.lower() + "_status", SystemLiteral), "comm_status"],
            list(map(lambda s: s.lower(), SystemLiteral)),
            ["esc"],
            ["time_lap", "hazard"],
            ["battery_fault", "esc_fault", "gps_fault", "motor_fault", "wheel_speed_fault"]
        ]
    uim.layout(layout)
    initialize_main()
    uim.show()
    return 0
