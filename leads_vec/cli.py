from datetime import datetime
from time import time
from typing import Callable

from customtkinter import CTkButton, CTkLabel, DoubleVar, StringVar, CTkSegmentedButton
from pynput.keyboard import Listener as _Listener, Key as _Key, KeyCode as _KeyCode

from leads import *
from leads.comm import *
from leads_gui import *
from leads_raspberry_pi import *
from leads_vec.__version__ import __version__


class CustomRuntimeData(RuntimeData):
    m1_mode: int = 0
    control_system_switch_changed: bool = False


def make_system_switch(ctx: LEADS, system: SystemLiteral, runtime_data: RuntimeData) -> Callable[[], None]:
    def switch() -> None:
        ctx.plugin(system).enabled(not ctx.plugin(system).enabled())
        runtime_data.control_system_switch_changed = True

    return switch


def format_lap_time(t: int) -> str:
    return f"{(t := int(t * .001)) // 60} MIN {t % 60} SEC"


def main() -> int:
    cfg = require_config()
    ctx = LEADS(data_seq_size=cfg.data_seq_size)
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

    def render(manager: ContextManager) -> None:
        def switch_m1_mode(_) -> None:
            manager.rd().m1_mode = (manager.rd().m1_mode + 1) % 3

        manager["m1"] = Typography(root, theme_key="CTkButton", variable=m1, clickable=True, command=switch_m1_mode,
                                   font=("Arial", cfg.font_size_small - 4)).lock_ratio(cfg.m_ratio)
        manager["m2"] = Speedometer(root, variable=speed).lock_ratio(cfg.m_ratio)
        manager["m3"] = ProxyCanvas(root, "CTkButton",
                                    Typography(root, theme_key="CTkButton", variable=voltage,
                                               font=("Arial", cfg.font_size_medium - 4)),
                                    SpeedTrendMeter(root, theme_key="CTkButton", variable=speed_trend,
                                                    font=("Arial", cfg.font_size_medium - 4)),
                                    GForceMeter(root, theme_key="CTkButton", variable=g_force,
                                                font=("Arial", cfg.font_size_medium - 4))).lock_ratio(cfg.m_ratio)

        manager["comm_status"] = CTkLabel(root, text="COMM OFFLINE", text_color="gray",
                                          font=("Arial", cfg.font_size_small))

        i = 0
        for system in SystemLiteral:
            i += 1
            system_lower = system.lower()
            manager[system_lower + "_status"] = CTkLabel(root, text=system + " READY", text_color="green",
                                                         font=("Arial", cfg.font_size_small))
            manager[system_lower] = CTkButton(root, text=system + " ON",
                                              command=make_system_switch(ctx, SystemLiteral(system), manager.rd()),
                                              font=("Arial", cfg.font_size_small))

        manager["left"] = CTkButton(root, text="", image=Left(cfg.font_size_large),
                                    command=lambda: ctx.left_indicator(not ctx.left_indicator()))
        manager["time_lap"] = CTkButton(root, text="", image=Stopwatch(), command=ctx.time_lap)
        manager["hazard"] = CTkButton(root, text="", image=Hazard(), command=lambda: ctx.hazard(not ctx.hazard()))
        manager["right"] = CTkButton(root, text="", image=Right(cfg.font_size_large),
                                     command=lambda: ctx.right_indicator(not ctx.right_indicator()))

        def switch_esc_mode(mode) -> None:
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
            elif msg == b"hazard":
                ctx.hazard(not ctx.hazard())

    uim.rd().comm = start_server(create_server(cfg.comm_port, CommCallback()), True)

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
                if has_device(GPS_RECEIVER):
                    gps = get_device(GPS_RECEIVER).read()
                    m1.set(f"GPS {"VALID" if d.gps_valid else "NO FIX"} - {gps[4]} {gps[5]}\n\n"
                           f"{d.gps_ground_speed:.1f} KM / H\n"
                           f"LAT {d.latitude:.5f}\nLON {d.longitude:.5f}")
                else:
                    m1.set(f"GPS {"VALID" if d.gps_valid else "NO FIX"} - !NF!\n\n"
                           f"{d.gps_ground_speed:.1f} KM / H\n"
                           f"LAT {d.latitude:.5f}\nLON {d.longitude:.5f}")
            elif uim.rd().m1_mode == 2:
                m1.set(f"VeC {__version__.upper()}\n\n"
                       f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n"
                       f"{(duration := int(time()) - uim.rd().start_time) // 60} MIN {duration % 60} SEC\n"
                       f"{(m := d.mileage):.1f} KM - {m * 3600 / duration:.1f} KM / H\n\n"
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

        def left_indicator(self, e: Event, state: bool) -> None:
            if has_device(LEFT_INDICATOR):
                get_device(LEFT_INDICATOR).write(LEDGroupCommand(
                    LEDCommand.BLINK, Transition("left2right", .1)
                ) if state else LEDGroupCommand(LEDCommand.OFF, Entire()))
            uim["left"].configure(image=Left(cfg.font_size_large, Color.RED if state else None))

        def right_indicator(self, e: Event, state: bool) -> None:
            if has_device(RIGHT_INDICATOR):
                get_device(RIGHT_INDICATOR).write(LEDGroupCommand(
                    LEDCommand.BLINK, Transition("right2left", .1)
                ) if state else LEDGroupCommand(LEDCommand.OFF, Entire()))
            uim["right"].configure(image=Right(cfg.font_size_large, Color.RED if state else None))

        def hazard(self, e: Event, state: bool) -> None:
            super().hazard(e, state)
            uim["hazard"].configure(image=Hazard(color=Color.RED if state else None))

    ctx.set_event_listener(CustomListener())
    uim["battery_fault"] = CTkLabel(root, text="")
    uim["brake_fault"] = CTkLabel(root, text="")
    uim["esc_fault"] = CTkLabel(root, text="")
    uim["gps_fault"] = CTkLabel(root, text="")
    uim["motor_fault"] = CTkLabel(root, text="")
    uim["wsc_fault"] = CTkLabel(root, text="")

    def on_fail(_, e: SuspensionEvent) -> None:
        if e.system == "BATT":
            uim["battery_fault"].configure(image=Battery(color=Color.RED))
        elif e.system == "BRAKE":
            uim["brake_fault"].configure(image=Brake(color=Color.RED))
        elif e.system == "ESC":
            uim["esc_fault"].configure(image=ESC(color=Color.RED))
        elif e.system == "GPS":
            uim["gps_fault"].configure(image=Satellite(color=Color.RED))
        elif e.system == "MOTOR":
            uim["motor_fault"].configure(image=Motor(color=Color.RED))
        elif e.system == "WSC":
            uim["wsc_fault"].configure(image=Speed(color=Color.RED))

    SFT.on_fail = on_fail

    def on_recover(_, e: SuspensionEvent) -> None:
        if e.system == "BATT":
            uim["battery_fault"].configure(image=None)
        elif e.system == "BRAKE":
            uim["brake_fault"].configure(image=None)
        elif e.system == "ESC":
            uim["esc_fault"].configure(image=None)
        elif e.system == "GPS":
            uim["gps_fault"].configure(image=None)
        elif e.system == "MOTOR":
            uim["motor_fault"].configure(image=None)
        elif e.system == "WSC":
            uim["wsc_fault"].configure(image=None)

    SFT.on_recover = on_recover
    if cfg.manual_mode:
        layout = [
            ["m1", "m2", "m3"],
            ["left", "time_lap", "hazard", "right"],
            [CTkLabel(root, text="MANUAL MODE"), CTkLabel(root, text="ASSISTANCE DISABLED"), "comm_status"],
            ["battery_fault", "brake_fault", "esc_fault", "gps_fault", "motor_fault", "wsc_fault"]
        ]
        ctx.esc_mode(ESCMode.OFF)
        uim.rd().control_system_switch_changed = True
    else:
        layout = [
            ["m1", "m2", "m3"],
            ["left", "time_lap", "hazard", "right"],
            ["battery_fault", "brake_fault", "esc_fault", "gps_fault", "motor_fault", "wsc_fault"],
            [*map(lambda s: s.lower() + "_status", SystemLiteral), "comm_status"],
            list(map(lambda s: s.lower(), SystemLiteral)),
            ["esc"]
        ]
    uim.layout(layout)
    root.grid_rowconfigure(2, weight=1)
    initialize_main()

    def on_press(key: _Key | _KeyCode) -> None:
        if key == _KeyCode.from_char("1"):
            make_system_switch(ctx, SystemLiteral.DTCS, uim.rd())()
        elif key == _KeyCode.from_char("2"):
            make_system_switch(ctx, SystemLiteral.ABS, uim.rd())()
        elif key == _KeyCode.from_char("3"):
            make_system_switch(ctx, SystemLiteral.EBI, uim.rd())()
        elif key == _KeyCode.from_char("4"):
            make_system_switch(ctx, SystemLiteral.ATBS, uim.rd())()
        elif key == _KeyCode.from_char("t"):
            ctx.time_lap()
        elif key == _Key.esc:
            uim.kill()

    _Listener(on_press=on_press).start()
    uim.show()
    return 0
