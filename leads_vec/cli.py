from datetime import datetime as _datetime
from threading import Thread as _Thread
from time import time as _time, sleep as _sleep
from typing import Callable as _Callable, override as _override

from customtkinter import CTkButton as _Button, CTkLabel as _Label, DoubleVar as _DoubleVar, StringVar as _StringVar, \
    CTkSegmentedButton as _CTkSegmentedButton
from pynput.keyboard import Listener as _Listener, Key as _Key, KeyCode as _KeyCode
from screeninfo import get_monitors as _get_monitors

from leads import LEADS, SystemLiteral, require_config, register_context, DTCS, ABS, EBI, ATBS, GPSSpeedCorrection, \
    ESCMode, get_controller, MAIN_CONTROLLER, L, EventListener, DataPushedEvent, UpdateEvent, has_device, \
    GPS_RECEIVER, get_device, InterventionEvent, SuspensionEvent, Event, LEFT_INDICATOR, RIGHT_INDICATOR, SFT, \
    initialize_main, format_duration, BRAKE_INDICATOR, REAR_VIEW_CAMERA, FRONT_VIEW_CAMERA, LEFT_VIEW_CAMERA, \
    RIGHT_VIEW_CAMERA
from leads.comm import Callback, Service, start_server, create_server, my_ip_addresses, ConnectionBase
from leads_audio import DIRECTION_INDICATOR_ON, DIRECTION_INDICATOR_OFF, WARNING, CONFIRM
from leads_gui import RuntimeData, Window, GForceVar, FrequencyGenerator, Left, Color, Right, ContextManager, \
    Typography, Speedometer, ProxyCanvas, SpeedTrendMeter, GForceMeter, Stopwatch, Hazard, initialize, Battery, Brake, \
    ESC, Satellite, Motor, Speed, Photo, Light, ImageVariable
from leads_vec.__version__ import __version__
from leads_video import get_camera


class CustomRuntimeData(RuntimeData):
    m1_mode: int = 0
    control_system_switch_changed: bool = False


def make_system_switch(ctx: LEADS, system: SystemLiteral, runtime_data: RuntimeData) -> _Callable[[], None]:
    def _() -> None:
        ctx.plugin(system).enabled(not ctx.plugin(system).enabled())
        runtime_data.control_system_switch_changed = True

    return _


def get_proxy_canvas(context_manager: ContextManager, key: str) -> ProxyCanvas:
    r = context_manager[key]
    if not isinstance(r, ProxyCanvas):
        raise TypeError(f"Widget \"{key}\" is supposed to be a proxy canvas")
    return r


class StreamCallback(Callback):
    def __init__(self, context_manager: ContextManager) -> None:
        super().__init__()
        self.uim: ContextManager = context_manager

    @_override
    def on_fail(self, service: Service, error: Exception) -> None:
        self.super(service=service, error=error)
        L.error(f"Comm stream server error: {repr(error)}")

    @_override
    def on_connect(self, service: Service, connection: ConnectionBase) -> None:
        self.super(service=service, connection=connection)
        self.uim["comm_stream_status"].configure(text="STM ONLINE", text_color=["black", "white"])

    @_override
    def on_disconnect(self, service: Service, connection: ConnectionBase) -> None:
        self.super(service=service, connection=connection)
        if self.uim.window().runtime_data().comm_stream.num_connections() < 2:
            self.uim["comm_stream_status"].configure(text="STM OFFLINE", text_color="gray")


def enable_comm_stream(context_manager: ContextManager, port: int) -> None:
    rd = context_manager.window().runtime_data()
    rd.comm_stream = start_server(create_server(port, StreamCallback(context_manager), b"end;"), True)

    def _() -> None:
        while True:
            if rd.comm_stream.num_connections() < 1:
                _sleep(.01)
            for tag in FRONT_VIEW_CAMERA, LEFT_VIEW_CAMERA, RIGHT_VIEW_CAMERA, REAR_VIEW_CAMERA:
                if (cam := get_camera(tag)) and (frame := cam.read_pil()):
                    rd.comm_stream_notify(tag, frame)

    _Thread(name="comm streamer", target=_, daemon=True).start()


class CommCallback(Callback):
    def __init__(self, context: LEADS, context_manager: ContextManager) -> None:
        super().__init__()
        self.ctx: LEADS = context
        self.uim: ContextManager = context_manager

    @_override
    def on_connect(self, service: Service, connection: ConnectionBase) -> None:
        self.super(service=service, connection=connection)
        self.uim["comm_status"].configure(text="COMM ONLINE", text_color=["black", "white"])

    @_override
    def on_disconnect(self, service: Service, connection: ConnectionBase) -> None:
        self.super(service=service, connection=connection)
        if self.uim.window().runtime_data().comm.num_connections() < 2:
            self.uim["comm_status"].configure(text="COMM OFFLINE", text_color="gray")

    @_override
    def on_fail(self, service: Service, error: Exception) -> None:
        self.super(service=service, error=error)
        L.error(f"Comm server error: {repr(error)}")

    @_override
    def on_receive(self, service: Service, msg: bytes) -> None:
        self.super(service=service, msg=msg)
        match msg:
            case b"time_lap":
                self.ctx.time_lap()
            case b"hazard":
                self.ctx.hazard(not self.ctx.hazard())
            case b"m1":
                get_proxy_canvas(self.uim, "m1").next_mode()
            case b"m3":
                get_proxy_canvas(self.uim, "m3").next_mode()


def add_secondary_window(context_manager: ContextManager, display: int, var_lap_times: _StringVar,
                         var_speed: _DoubleVar) -> None:
    root_window = context_manager.window()
    w = Window(0, 0, root_window.refresh_rate(), root_window.runtime_data(), display=display)
    window_index = context_manager.add_window(w)
    num_widgets = int(w.width() / w.height())
    widgets = [Speedometer(w.root(), "CTkLabel", height=w.height(), variable=var_speed, style=1,
                           font=(("Arial", int(w.width() * .1)),) * 3, next_style_on_click=False)]
    if num_widgets >= 2:
        widgets.append(Typography(w.root(), height=w.height(), variable=var_lap_times,
                                  font=("Arial", int(w.width() * .04))))
    context_manager.layout([widgets], 0, window_index)


def main() -> int:
    cfg = require_config()
    ctx = LEADS(data_seq_size=cfg.data_seq_size, num_laps_timed=cfg.num_laps_timed)
    register_context(ctx)
    ctx.plugin(SystemLiteral.DTCS, DTCS())
    ctx.plugin(SystemLiteral.ABS, ABS())
    ctx.plugin(SystemLiteral.EBI, EBI())
    ctx.plugin(SystemLiteral.ATBS, ATBS())
    ctx.plugin("GPS_SPEED_CORRECTION", GPSSpeedCorrection())
    w = Window(cfg.width, cfg.height, cfg.refresh_rate, CustomRuntimeData(), fullscreen=cfg.fullscreen,
               no_title_bar=cfg.no_title_bar, theme_mode=cfg.theme_mode)
    root = w.root()
    root.configure(cursor="dot")
    var_lap_times = _StringVar(root, "")
    var_gps = _StringVar(root, "")
    var_rear_view = ImageVariable(root, None)
    var_info = _StringVar(root, "")
    var_speed = _DoubleVar(root, 0)
    var_voltage = _StringVar(root, "")
    var_speed_trend = _DoubleVar(root, 0)
    var_g_force = GForceVar(root, 0, 0)
    var_esc = _StringVar(root, "STANDARD")

    class LeftIndicator(FrequencyGenerator):
        @_override
        def do(self) -> None:
            uim["left"].configure(image=Left(cfg.font_size_large, Color.RED if self._loops % 2 == 1 else None))

    class RightIndicator(FrequencyGenerator):
        @_override
        def do(self) -> None:
            uim["right"].configure(image=Right(cfg.font_size_large, Color.RED if self._loops % 2 == 1 else None))

    class DirectionIndicatorSound(FrequencyGenerator):
        @_override
        def do(self) -> None:
            if self._loops % 2 == 1:
                DIRECTION_INDICATOR_ON.play()
            else:
                DIRECTION_INDICATOR_OFF.play()

    def render(manager: ContextManager) -> None:
        m1_widgets = (
            Typography(root, theme_key="CTkButton", variable=var_lap_times,
                       font=("Arial", cfg.font_size_small)),
            Typography(root, theme_key="CTkButton", variable=var_gps,
                       font=("Arial", cfg.font_size_small)),
            Typography(root, theme_key="CTkButton", variable=var_info,
                       font=("Arial", cfg.font_size_small - 4))
        )
        if has_device(REAR_VIEW_CAMERA):
            m1_widgets += (Photo(root, theme_key="CTkButton", variable=var_rear_view),)
        manager["m1"] = ProxyCanvas(root, "CTkButton", *m1_widgets).lock_ratio(cfg.m_ratio)
        manager["m2"] = Speedometer(root, variable=var_speed).lock_ratio(cfg.m_ratio)
        manager["m3"] = ProxyCanvas(root, "CTkButton",
                                    Typography(root, theme_key="CTkButton", variable=var_voltage,
                                               font=("Arial", cfg.font_size_medium - 4)),
                                    SpeedTrendMeter(root, theme_key="CTkButton", variable=var_speed_trend,
                                                    font=("Arial", cfg.font_size_medium - 4)),
                                    GForceMeter(root, theme_key="CTkButton", variable=var_g_force,
                                                font=("Arial", cfg.font_size_medium - 4))
                                    ).lock_ratio(cfg.m_ratio)

        manager["comm_status"] = _Label(root, text="COMM OFFLINE", text_color="gray",
                                        font=("Arial", cfg.font_size_small))
        if cfg.comm_stream:
            manager["comm_stream_status"] = _Label(root, text="STM OFFLINE", text_color="gray",
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

        manager["esc"] = _CTkSegmentedButton(root, values=["STANDARD", "AGGRESSIVE", "SPORT", "OFF"], variable=var_esc,
                                             command=switch_esc_mode, font=("Arial", cfg.font_size_small))

    uim = initialize(w, render, ctx, get_controller(MAIN_CONTROLLER))

    w.runtime_data().comm = start_server(create_server(cfg.comm_port, CommCallback(ctx, uim)), True)
    if cfg.comm_stream:
        enable_comm_stream(uim, cfg.comm_stream_port)

    class CustomListener(EventListener):
        @_override
        def pre_push(self, e: DataPushedEvent) -> None:
            self.super(e)
            d = e.data.to_dict()
            m1, m3 = get_proxy_canvas(uim, "m1"), get_proxy_canvas(uim, "m3")
            d["speed_trend"] = ctx.speed_trend()
            d["lap_times"] = ctx.lap_times()
            d["m1_mode"] = m1.mode()
            d["m3_mode"] = m3.mode()
            w.runtime_data().comm_notify(d)

        @_override
        def on_update(self, e: UpdateEvent) -> None:
            self.super(e)
            d = e.context.data()
            lap_times = ctx.lap_times()
            var_lap_times.set(f"LAP TIMES\n\n{"No Lap Timed" if len(lap_times) < 1 else "\n".join(map(
                lambda t: format_duration(t * .001), lap_times))}")
            if has_device(GPS_RECEIVER):
                gps = get_device(GPS_RECEIVER).read()
                var_gps.set(f"GPS {"VALID" if d.gps_valid else "NO FIX"} - {gps[4]} {gps[5]}\n\n"
                            f"{d.gps_ground_speed:.1f} KM / H\n"
                            f"LAT {d.latitude:.5f}\nLON {d.longitude:.5f}")
            else:
                var_gps.set(f"GPS {"VALID" if d.gps_valid else "NO FIX"} - !NF!\n\n"
                            f"{d.gps_ground_speed:.1f} KM / H\n"
                            f"LAT {d.latitude:.5f}\nLON {d.longitude:.5f}")
            if cam := get_camera(REAR_VIEW_CAMERA):
                var_rear_view.set(cam.read_pil())
            var_info.set(f"VeC {__version__.upper()}\n\n"
                         f"{_datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n"
                         f"{format_duration(duration := _time() - w.runtime_data().start_time)}\n"
                         f"{(m := d.mileage):.1f} KM - {m * 3600 / duration:.1f} KM / H\n\n"
                         f"{cfg.refresh_rate} - {w.fps():.2f} FPS - {w.net_delay() * 1000:.1f} MS\n"
                         f"{(["NOT FOUND"] + my_ip_addresses())[-1]}:{w.runtime_data().comm.port()}")
            var_speed.set(d.speed)
            var_voltage.set(f"{d.voltage:.1f} V")
            st = ctx.speed_trend()
            var_speed_trend.set(st)
            var_g_force.set((d.lateral_acceleration, d.forward_acceleration))
            if w.runtime_data().control_system_switch_changed:
                for system in SystemLiteral:
                    system_lowercase = system.lower()
                    if ctx.plugin(SystemLiteral(system)).enabled():
                        uim[system_lowercase].configure(text=f"{system} ON")
                    else:
                        uim[system_lowercase].configure(text=f"{system} OFF")
                        uim[f"{system_lowercase}_status"].configure(text=f"{system} OFF", text_color=("black", "white"))
                w.runtime_data().control_system_switch_changed = False

        @_override
        def pre_intervene(self, e: InterventionEvent) -> None:
            self.super(e)
            if e.system in SystemLiteral:
                uim[f"{e.system.lower()}_status"].configure(text=f"{e.system} INTEV", text_color="red")

        @_override
        def post_intervene(self, e: InterventionEvent) -> None:
            self.super(e)
            if e.system in SystemLiteral:
                uim[f"{e.system.lower()}_status"].configure(text=f"{e.system} READY", text_color="green")

        @_override
        def pre_suspend(self, e: SuspensionEvent) -> None:
            self.super(e)
            if e.system in SystemLiteral:
                uim[f"{e.system.lower()}_status"].configure(text=f"{e.system} SUSPD", text_color="gray")

        @_override
        def post_suspend(self, e: SuspensionEvent) -> None:
            self.super(e)
            if e.system in SystemLiteral:
                uim[f"{e.system.lower()}_status"].configure(text=f"{e.system} READY", text_color="green")

        @_override
        def brake_indicator(self, event: Event, state: bool) -> None:
            if has_device(BRAKE_INDICATOR):
                get_device(BRAKE_INDICATOR).write(state)

        @_override
        def left_indicator(self, e: Event, state: bool) -> None:
            if has_device(LEFT_INDICATOR):
                get_device(LEFT_INDICATOR).write(state)
            if state:
                w.add_frequency_generator("left_indicator", LeftIndicator(500))
                w.add_frequency_generator("direction_indicator_sound", DirectionIndicatorSound(500))
            else:
                w.remove_frequency_generator("left_indicator")
                w.remove_frequency_generator("direction_indicator_sound")
                uim["left"].configure(image=Left(cfg.font_size_large, None))

        @_override
        def right_indicator(self, e: Event, state: bool) -> None:
            if has_device(RIGHT_INDICATOR):
                get_device(RIGHT_INDICATOR).write(state)
            if state:
                w.add_frequency_generator("right_indicator", RightIndicator(500))
                w.add_frequency_generator("direction_indicator_sound", DirectionIndicatorSound(500))
            else:
                w.remove_frequency_generator("right_indicator")
                w.remove_frequency_generator("direction_indicator_sound")
                uim["right"].configure(image=Right(cfg.font_size_large, None))

        @_override
        def hazard(self, e: Event, state: bool) -> None:
            super().hazard(e, state)
            uim["hazard"].configure(image=Hazard(color=Color.RED if state else None))

    ctx.set_event_listener(CustomListener())
    uim["battery_fault"] = _Label(root, text="")
    uim["brake_fault"] = _Label(root, text="")
    uim["esc_fault"] = _Label(root, text="")
    uim["gps_fault"] = _Label(root, text="")
    uim["light_fault"] = _Label(root, text="")
    uim["motor_fault"] = _Label(root, text="")
    uim["wsc_fault"] = _Label(root, text="")

    def on_fail(e: SuspensionEvent) -> None:
        match e.system:
            case "BATT":
                uim["battery_fault"].configure(image=Battery(color=Color.RED))
            case "BRAKE":
                uim["brake_fault"].configure(image=Brake(color=Color.RED))
            case "ESC":
                uim["esc_fault"].configure(image=ESC(color=Color.RED))
            case "GPS":
                uim["gps_fault"].configure(image=Satellite(color=Color.RED))
            case "LIGHT":
                uim["light_fault"].configure(image=Light(color=Color.RED))
            case "MOTOR":
                uim["motor_fault"].configure(image=Motor(color=Color.RED))
            case "WSC":
                uim["wsc_fault"].configure(image=Speed(color=Color.RED))

    SFT.on_fail = on_fail

    def on_recover(e: SuspensionEvent) -> None:
        match e.system:
            case "BATT":
                uim["battery_fault"].configure(image=None)
            case "BRAKE":
                uim["brake_fault"].configure(image=None)
            case "ESC":
                uim["esc_fault"].configure(image=None)
            case "GPS":
                uim["gps_fault"].configure(image=None)
            case "LIGHT":
                uim["light_fault"].configure(image=None)
            case "MOTOR":
                uim["motor_fault"].configure(image=None)
            case "WSC":
                uim["wsc_fault"].configure(image=None)

    SFT.on_recover = on_recover
    meters = ["m1", "m2", "m3"]
    buttons = ["left", "time_lap", "hazard", "right"]
    fault_lights = ["battery_fault", "brake_fault", "esc_fault", "gps_fault", "light_fault", "motor_fault", "wsc_fault"]
    conditional_statuses = ("comm_stream_status",) if cfg.comm_stream else ()
    if cfg.manual_mode:
        layout = [
            meters, buttons,
            [_Label(root, text="MANUAL MODE"), _Label(root, text="ASSISTANCE DISABLED"), "comm_status",
             *conditional_statuses],
            fault_lights
        ]
        ctx.esc_mode(ESCMode.OFF)
        w.runtime_data().control_system_switch_changed = True
    else:
        layout = [
            meters, buttons, fault_lights,
            [*map(lambda s: f"{s.lower()}_status", SystemLiteral), "comm_status", *conditional_statuses],
            list(map(lambda s: s.lower(), SystemLiteral)),
            ["esc"]
        ]
    uim.layout(layout)
    for i in range(min(cfg.num_external_screens, len(_get_monitors()) - 1)):
        add_secondary_window(uim, i + 1, var_lap_times, var_speed)
    root.grid_rowconfigure(2, weight=1)
    initialize_main()

    def on_press(key: _Key | _KeyCode) -> None:
        if isinstance(key, _Key):
            return
        match key.char:
            case "1":
                make_system_switch(ctx, SystemLiteral.DTCS, w.runtime_data())()
            case "2":
                make_system_switch(ctx, SystemLiteral.ABS, w.runtime_data())()
            case "3":
                make_system_switch(ctx, SystemLiteral.EBI, w.runtime_data())()
            case "4":
                make_system_switch(ctx, SystemLiteral.ATBS, w.runtime_data())()
            case "t":
                ctx.time_lap()

    _Listener(on_press=on_press).start()
    uim.show()
    return 0
