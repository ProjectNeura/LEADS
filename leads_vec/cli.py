from datetime import datetime
from time import time

from customtkinter import CTkButton, CTkLabel
from keyboard import add_hotkey

from leads import *
from leads.config import *
from leads.comm import *
from leads_gui import *
from leads_vec.__version__ import __version__


class CustomRuntimeData(RuntimeData):
    m1_mode: int = 0
    m3_mode: int = 0


def main() -> int:
    cfg = get_config(Config)
    context = Leads(srw_mode=cfg.srw_mode)
    window = Window(cfg.width,
                    cfg.height,
                    cfg.refresh_rate,
                    CustomRuntimeData(),
                    fullscreen=cfg.fullscreen,
                    no_title_bar=cfg.no_title_bar)

    def render(manager: ContextManager):
        def switch_m1_mode():
            manager.rd().m1_mode = (manager.rd().m1_mode + 1) % 2

        def switch_m3_mode():
            manager.rd().m3_mode = (manager.rd().m3_mode + 1) % 3

        manager["m1"] = CTkButton(window.root(), font=("Arial", cfg.font_size_small), key=switch_m1_mode,
                                  size=(round(manager.window().width() * cfg.scaling_factor / 21), 13))
        manager["m2"] = CTkButton(window.root(), font=("Arial", cfg.font_size_x_large),
                                  size=(round(manager.window().width() * cfg.scaling_factor / 126), 2))
        manager["m3"] = CTkButton(window.root(), font=("Arial", cfg.font_size_medium), key=switch_m3_mode,
                                  size=(round(manager.window().width() * cfg.scaling_factor / 42), 7))
        manager["dtcs_status"] = CTkLabel(window.root(), text="DTCS READY", text_color="green",
                                          font=("Arial", cfg.font_size_small),
                                          size=(round(manager.window().width() * cfg.scaling_factor / 40), None))
        manager["abs_status"] = CTkLabel(window.root(), text="ABS READY", text_color="green",
                                         font=("Arial", cfg.font_size_small),
                                         size=(round(manager.window().width() * cfg.scaling_factor / 40), None))
        manager["ebi_status"] = CTkLabel(window.root(), text="EBI READY", text_color="green",
                                         font=("Arial", cfg.font_size_small),
                                         size=(round(manager.window().width() * cfg.scaling_factor / 40), None))
        manager["atbs_status"] = CTkLabel(window.root(), text="ATBS READY", text_color="green",
                                          font=("Arial", cfg.font_size_small),
                                          size=(round(manager.window().width() * cfg.scaling_factor / 40), None))
        manager["comm_status"] = CTkLabel(window.root(), text="COMM OFFLINE", text_color="gray",
                                          font=("Arial", cfg.font_size_small),
                                          size=(round(manager.window().width() * cfg.scaling_factor / 40), None))

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

        manager["dtcs"] = CTkButton(window.root(), button_text="DTCS ON", key=switch_dtcs,
                                    font=("Arial", cfg.font_size_small),
                                    size=(round(manager.window().width() * cfg.scaling_factor / 35), 1))
        manager["abs"] = CTkButton(window.root(), button_text="ABS ON", key=switch_abs,
                                   font=("Arial", cfg.font_size_small),
                                   size=(round(manager.window().width() * cfg.scaling_factor / 35), 1))
        manager["ebi"] = CTkButton(window.root(), button_text="EBI ON", key=switch_ebi,
                                   font=("Arial", cfg.font_size_small),
                                   size=(round(manager.window().width() * cfg.scaling_factor / 35), 1))
        manager["atbs"] = CTkButton(window.root(), button_text="ATBS ON", key=switch_atbs,
                                    font=("Arial", cfg.font_size_small),
                                    size=(round(manager.window().width() * cfg.scaling_factor / 35), 1))

    uim = initialize(window, render, context, get_controller(MAIN_CONTROLLER))

    class CommCallback(Callback):
        def on_fail(self, service: Service, error: Exception) -> None:
            L.error("Comm server error: " + str(error))

        def on_connect(self, service: Service, connection: Connection) -> None:
            uim["comm_status"].config(text="COMM ONLINE", text_color="black")

    uim.rd().comm = start_server(create_server(cfg.comm_port, CommCallback()), True)

    class CustomListener(EventListener):
        def on_push(self, e: DataPushedEvent) -> None:
            uim.rd().comm_notify(e.data)

        def on_update(self, e: UpdateEvent) -> None:
            duration = int(time()) - uim.rd().start_time
            if uim.rd().m1_mode == 0:
                uim["m1"].config(button_text="LAP TIME\n\nLAP1 9s\nLAP2 11s\nLAP3 10s")
            elif uim.rd().m1_mode == 1:
                uim["m1"].config(button_text=f"VeC {__version__.upper()}\n\n"
                                 f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                                 f"{duration // 60} MIN {duration % 60} SEC\n\n"
                                 f"{'SRW MODE' if cfg.srw_mode else 'DRW MODE'}\n"
                                 f"REFRESH RATE: {cfg.refresh_rate} FPS")
            if uim.rd().frame_counter % int(cfg.refresh_rate / 4) == 0:
                uim["m2"].config(button_text=f"{int(context.data().front_wheel_speed)}")
            if uim.rd().m3_mode == 0:
                uim["m3"].config(button_text="0.0V")
            elif uim.rd().m3_mode == 1:
                uim["m3"].config(button_text="G Force")
            else:
                uim["m3"].config(button_text="Speed Trend")
            if uim.rd().comm.num_connections() < 1:
                uim["comm_status"].config(text="COMM OFFLINE", text_color="gray")

        def on_intervene(self, e: InterventionEvent) -> None:
            uim[e.system.lower() + "_status"].config(text=e.system + " INTEV", text_color="purple")

        def post_intervene(self, e: InterventionEvent) -> None:
            uim[e.system.lower() + "_status"].config(text=e.system + " READY", text_color="green")

        def on_suspend(self, e: SuspensionEvent) -> None:
            uim[e.system.lower() + "_status"].config(text=e.system + " SUSPD", text_color="red")

        def post_suspend(self, e: SuspensionEvent) -> None:
            uim[e.system.lower() + "_status"].config(text=e.system + " READY", text_color="green")

    context.set_event_listener(CustomListener())
    uim.layout([
        ["m1", "m2", "m3"],
        ["dtcs_status", "abs_status", "ebi_status", "atbs_system", "comm_status"],
        ["dtcs", "abs", "ebi", "atbs"]
    ])
    uim.show()
    uim.rd().comm_kill()
    return 0
