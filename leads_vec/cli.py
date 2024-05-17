from datetime import datetime as _datetime
from time import time as _time
from typing import Callable as _Callable

from customtkinter import CTkButton as _Button, CTkLabel as _Label, DoubleVar as _DoubleVar, StringVar as _StringVar, \
    CTkSegmentedButton as _CTkSegmentedButton
from pynput.keyboard import Listener as _Listener, Key as _Key, KeyCode as _KeyCode

from leads import LEADS, SystemLiteral, require_config, register_context, DTCS, ABS, EBI, ATBS, GPSSpeedCorrection, \
    ESCMode, get_controller, MAIN_CONTROLLER, L, EventListener, DataPushedEvent, UpdateEvent, has_device, \
    GPS_RECEIVER, get_device, InterventionEvent, SuspensionEvent, Event, LEFT_INDICATOR, RIGHT_INDICATOR, SFT, \
    initialize_main, format_duration
from leads.comm import Callback, Service, start_server, create_server, my_ip_addresses
from leads_audio import DIRECTION_INDICATOR_ON, DIRECTION_INDICATOR_OFF, WARNING, CONFIRM
from leads_gui import RuntimeData, Window, GForceVar, FrequencyGenerator, Left, Color, Right, ContextManager, \
    Typography, Speedometer, ProxyCanvas, SpeedTrendMeter, GForceMeter, Stopwatch, Hazard, initialize, Battery, Brake, \
    ESC, Satellite, Motor, Speed
from leads_raspberry_pi import LEDGroupCommand, LEDCommand, Transition, Entire
from leads_vec.__version__ import __version__


class CustomRuntimeData(RuntimeData):
    m1_mode: int = 0
    control_system_switch_changed: bool = False


def make_system_switch(ctx: LEADS, system: SystemLiteral, runtime_data: RuntimeData) -> _Callable[[], None]:
    def switch() -> None:
        ctx.plugin(system).enabled(not ctx.plugin(system).enabled())
        runtime_data.control_system_switch_changed = True

    return switch


def main() -> int:
    cfg = require_config()
    ctx = LEADS(data_seq_size=cfg.data_seq_size, num_laps_timed=cfg.num_laps_timed)
    register_context(ctx)
    ctx.plugin(SystemLiteral.DTCS, DTCS())
    ctx.plugin(SystemLiteral.ABS, ABS())
    ctx.plugin(SystemLiteral.EBI, EBI())
    ctx.plugin(SystemLiteral.ATBS, ATBS())
    ctx.plugin("GPS_SPEED_CORRECTION", GPSSpeedCorrection())
    w = Window(cfg.width,
               cfg.height,
               cfg.refresh_rate,
               CustomRuntimeData(),
               fullscreen=cfg.fullscreen,
               no_title_bar=cfg.no_title_bar,
               theme_mode=cfg.theme_mode)
    root = w.root()
    root.configure(cursor="dot")
    m1 = _StringVar(root, "")
    speed = _DoubleVar(root, 0)
    voltage = _StringVar(root, "")
    speed_trend = _DoubleVar(root, 0)
    g_force = GForceVar(root, 0, 0)
    esc = _StringVar(root, "STANDARD")

    class LeftIndicator(FrequencyGenerator):
        def do(self) -> None:
            uim["left"].configure(image=Left(cfg.font_size_large, Color.RED if self._loops % 2 == 1 else None))

    class RightIndicator(FrequencyGenerator):
        def do(self) -> None:
            uim["right"].configure(image=Right(cfg.font_size_large, Color.RED if self._loops % 2 == 1 else None))

    class DirectionIndicatorSound(FrequencyGenerator):
        def do(self) -> None:
            if self._loops % 2 == 1:
                DIRECTION_INDICATOR_ON.play()
            else:
                DIRECTION_INDICATOR_OFF.play()

    def render(manager: ContextManager) -> None:
        def switch_m1_mode(_) -> None:
            w.runtime_data().m1_mode = (w.runtime_data().m1_mode + 1) % 3

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

        manager["comm_status"] = _Label(root, text="COMM OFFLINE", text_color="gray",
                                        font=("Arial", cfg.font_size_small))

        i = 0
        for system in SystemLiteral:
            i += 1
            system_lower = system.lower()
            manager[f"{system_lower}_status"] = _Label(root, text=f"{system} READY", text_color="green",
                                                       font=("Arial", cfg.font_size_small))
            manager[system_lower] = _Button(root, text=f"{system} ON",
                                            command=make_system_switch(ctx, SystemLiteral(system), w.runtime_data()),
                                            font=("Arial", cfg.font_size_small))

        manager["left"] = _Button(root, text="", image=Left(cfg.font_size_large),
                                  command=lambda: ctx.left_indicator(not ctx.left_indicator()))
        manager["right"] = _Button(root, text="", image=Right(cfg.font_size_large),
                                   command=lambda: ctx.right_indicator(not ctx.right_indicator()))

        def time_lap() -> None:
            ctx.time_lap()
            CONFIRM.play()

        manager["time_lap"] = _Button(root, text="", image=Stopwatch(), command=time_lap)
        manager["hazard"] = _Button(root, text="", image=Hazard(), command=lambda: ctx.hazard(not ctx.hazard()))

        def switch_esc_mode(mode: str) -> None:
            if (esc_mode := ESCMode[mode]) < 2:
                manager["esc"].configure(selected_color="green", selected_hover_color="green")
            else:
                manager["esc"].configure(selected_color="red", selected_hover_color="red")
                WARNING.play()
            ctx.esc_mode(esc_mode)
            w.runtime_data().control_system_switch_changed = True

        manager["esc"] = _CTkSegmentedButton(root, values=["STANDARD", "AGGRESSIVE", "SPORT", "OFF"], variable=esc,
                                             command=switch_esc_mode, font=("Arial", cfg.font_size_small))

    uim = initialize(w, render, ctx, get_controller(MAIN_CONTROLLER))

    class CommCallback(Callback):
        def on_fail(self, service: Service, error: Exception) -> None:
            self.super(service=service, error=error)
            L.error(f"Comm server error: {repr(error)}")

        def on_receive(self, service: Service, msg: bytes) -> None:
            self.super(service=service, msg=msg)
            if msg == b"time_lap":
                ctx.time_lap()
            elif msg == b"hazard":
                ctx.hazard(not ctx.hazard())

    w.runtime_data().comm = start_server(create_server(cfg.comm_port, CommCallback()), True)

    class CustomListener(EventListener):
        def pre_push(self, e: DataPushedEvent) -> None:
            self.super(e)
            d = e.data.to_dict()
            d["speed_trend"] = ctx.speed_trend()
            d["lap_times"] = ctx.lap_time_list()
            w.runtime_data().comm_notify(d)

        def on_update(self, e: UpdateEvent) -> None:
            self.super(e)
            d = e.context.data()
            if w.runtime_data().m1_mode == 0:
                lap_time_list = ctx.lap_time_list()
                m1.set(f"LAP TIMES\n\n{"No Lap Timed" if len(lap_time_list) < 1 else "\n".join(
                    map(lambda t: format_duration(t * .001), lap_time_list))}")
            elif w.runtime_data().m1_mode == 1:
                if has_device(GPS_RECEIVER):
                    gps = get_device(GPS_RECEIVER).read()
                    m1.set(f"GPS {"VALID" if d.gps_valid else "NO FIX"} - {gps[4]} {gps[5]}\n\n"
                           f"{d.gps_ground_speed:.1f} KM / H\n"
                           f"LAT {d.latitude:.5f}\nLON {d.longitude:.5f}")
                else:
                    m1.set(f"GPS {"VALID" if d.gps_valid else "NO FIX"} - !NF!\n\n"
                           f"{d.gps_ground_speed:.1f} KM / H\n"
                           f"LAT {d.latitude:.5f}\nLON {d.longitude:.5f}")
            elif w.runtime_data().m1_mode == 2:
                m1.set(f"VeC {__version__.upper()}\n\n"
                       f"{_datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n"
                       f"{format_duration(duration := _time() - w.runtime_data().start_time)}\n"
                       f"{(m := d.mileage):.1f} KM - {m * 3600 / duration:.1f} KM / H\n\n"
                       f"{cfg.refresh_rate} - {w.fps():.2f} FPS - {w.net_delay() * 1000:.1f} MS\n"
                       f"{ip[-1] if len(ip := my_ip_addresses()) > 0 else "NOT FOUND"}:{w.runtime_data().comm.port()}")
            speed.set(d.speed)
            voltage.set(f"{d.voltage:.1f} V")
            st = ctx.speed_trend()
            speed_trend.set(st)
            g_force.set((d.lateral_acceleration, d.forward_acceleration))
            if w.runtime_data().comm.num_connections() < 1:
                uim["comm_status"].configure(text="COMM OFFLINE", text_color="gray")
            else:
                uim["comm_status"].configure(text="COMM ONLINE", text_color=["black", "white"])
            if w.runtime_data().control_system_switch_changed:
                for system in SystemLiteral:
                    system_lowercase = system.lower()
                    if ctx.plugin(SystemLiteral(system)).enabled():
                        uim[system_lowercase].configure(text=f"{system} ON")
                    else:
                        uim[system_lowercase].configure(text=f"{system} OFF")
                        uim[f"{system_lowercase}_status"].configure(text=f"{system} OFF", text_color=("black", "white"))
                w.runtime_data().control_system_switch_changed = False

        def pre_intervene(self, e: InterventionEvent) -> None:
            self.super(e)
            if e.system in SystemLiteral:
                uim[f"{e.system.lower()}_status"].configure(text=f"{e.system} INTEV", text_color="red")

        def post_intervene(self, e: InterventionEvent) -> None:
            self.super(e)
            if e.system in SystemLiteral:
                uim[f"{e.system.lower()}_status"].configure(text=f"{e.system} READY", text_color="green")

        def pre_suspend(self, e: SuspensionEvent) -> None:
            self.super(e)
            if e.system in SystemLiteral:
                uim[f"{e.system.lower()}_status"].configure(text=f"{e.system} SUSPD", text_color="gray")

        def post_suspend(self, e: SuspensionEvent) -> None:
            self.super(e)
            if e.system in SystemLiteral:
                uim[f"{e.system.lower()}_status"].configure(text=f"{e.system} READY", text_color="green")

        def left_indicator(self, e: Event, state: bool) -> None:
            if has_device(LEFT_INDICATOR):
                get_device(LEFT_INDICATOR).write(LEDGroupCommand(
                    LEDCommand.BLINK, Transition("left2right", 100)
                ) if state else LEDGroupCommand(LEDCommand.OFF, Entire()))
            if state:
                w.add_frequency_generator("left_indicator", LeftIndicator(500))
                w.add_frequency_generator("direction_indicator_sound", DirectionIndicatorSound(500))
            else:
                w.remove_frequency_generator("left_indicator")
                w.remove_frequency_generator("direction_indicator_sound")
                uim["left"].configure(image=Left(cfg.font_size_large, None))

        def right_indicator(self, e: Event, state: bool) -> None:
            if has_device(RIGHT_INDICATOR):
                get_device(RIGHT_INDICATOR).write(LEDGroupCommand(
                    LEDCommand.BLINK, Transition("right2left", 100)
                ) if state else LEDGroupCommand(LEDCommand.OFF, Entire()))
            if state:
                w.add_frequency_generator("right_indicator", RightIndicator(500))
                w.add_frequency_generator("direction_indicator_sound", DirectionIndicatorSound(500))
            else:
                w.remove_frequency_generator("right_indicator")
                w.remove_frequency_generator("direction_indicator_sound")
                uim["right"].configure(image=Right(cfg.font_size_large, None))

        def hazard(self, e: Event, state: bool) -> None:
            super().hazard(e, state)
            uim["hazard"].configure(image=Hazard(color=Color.RED if state else None))

    ctx.set_event_listener(CustomListener())
    uim["battery_fault"] = _Label(root, text="")
    uim["brake_fault"] = _Label(root, text="")
    uim["esc_fault"] = _Label(root, text="")
    uim["gps_fault"] = _Label(root, text="")
    uim["motor_fault"] = _Label(root, text="")
    uim["wsc_fault"] = _Label(root, text="")

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
            [_Label(root, text="MANUAL MODE"), _Label(root, text="ASSISTANCE DISABLED"), "comm_status"],
            ["battery_fault", "brake_fault", "esc_fault", "gps_fault", "motor_fault", "wsc_fault"]
        ]
        ctx.esc_mode(ESCMode.OFF)
        w.runtime_data().control_system_switch_changed = True
    else:
        layout = [
            ["m1", "m2", "m3"],
            ["left", "time_lap", "hazard", "right"],
            ["battery_fault", "brake_fault", "esc_fault", "gps_fault", "motor_fault", "wsc_fault"],
            [*map(lambda s: f"{s.lower()}_status", SystemLiteral), "comm_status"],
            list(map(lambda s: s.lower(), SystemLiteral)),
            ["esc"]
        ]
    uim.layout(layout)
    root.grid_rowconfigure(2, weight=1)
    initialize_main()

    def on_press(key: _Key | _KeyCode) -> None:
        if key == _KeyCode.from_char("1"):
            make_system_switch(ctx, SystemLiteral.DTCS, w.runtime_data())()
        elif key == _KeyCode.from_char("2"):
            make_system_switch(ctx, SystemLiteral.ABS, w.runtime_data())()
        elif key == _KeyCode.from_char("3"):
            make_system_switch(ctx, SystemLiteral.EBI, w.runtime_data())()
        elif key == _KeyCode.from_char("4"):
            make_system_switch(ctx, SystemLiteral.ATBS, w.runtime_data())()
        elif key == _KeyCode.from_char("t"):
            ctx.time_lap()
        elif key == _Key.esc:
            uim.kill()

    _Listener(on_press=on_press).start()
    uim.show()
    return 0
