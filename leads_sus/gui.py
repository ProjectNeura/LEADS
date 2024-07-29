from customtkinter import StringVar as _StringVar

from leads_gui import Window as _Window, ContextManager as _ContextManager, Typography as _Typography

_user_window_index: int = -1


def show_or_hide_user_window(context_manager: _ContextManager, var_user: _StringVar) -> None:
    global _user_window_index
    if _user_window_index >= 0:
        context_manager.window(_user_window_index).hide()
    root_window = context_manager.window()
    rd = root_window.runtime_data()
    w = _Window(int(root_window.width() * .8), int(root_window.height() * .8), root_window.refresh_rate(), rd,
                fullscreen=False, display=root_window.screen_index())
    window_index = context_manager.add_window(w)
    _user_window_index = window_index
    context_manager["current_user_profile"] = _Typography(w.root(), height=100, variable=var_user)
    context_manager.layout([["current_user_profile"]], window_index=window_index)
