from tkinter import Misc as _Misc
from typing import override as _override

from customtkinter import StringVar as _StringVar

from leads import require_config as _require_config
from leads_gui import Window as _Window, ContextManager as _ContextManager, CanvasBased as _CanvasBased, \
    TextBased as _TextBased, VariableControlled as _VariableControlled
from leads_gui.types import Font as _Font, Color as _Color
from leads_sus.user import list_users, list_user_names


class UserChooser(_TextBased, _VariableControlled):
    def __init__(self,
                 master: _Misc,
                 theme_key: str = "CTkButton",
                 width: float = 0,
                 height: float = 0,
                 variable: _StringVar | None = None,
                 font: tuple[_Font, _Font] | None = None,
                 text_color: _Color | None = None,
                 fg_color: _Color | None = None,
                 hover_color: _Color | None = None,
                 bg_color: _Color | None = None,
                 corner_radius: float | None = None) -> None:
        _TextBased.__init__(self, master, theme_key, width, height, None, text_color, fg_color, hover_color, bg_color,
                            corner_radius, True, lambda _: self.next_user())
        _VariableControlled.__init__(self, variable if variable else _StringVar(master))
        self.attach(self.partially_render)
        cfg = _require_config()
        self._font: tuple[_Font, _Font] = font if font else (("Arial", cfg.font_size_large),
                                                             ("Arial", cfg.font_size_medium))
        self._index: int = -1

    def next_user(self) -> None:
        user_names = list_user_names()
        self._variable.set(user_names[(user_names.index(self._variable.get()) + 1) % len(user_names)])

    @_override
    def dynamic_renderer(self, canvas: _CanvasBased) -> None:
        canvas.clear("d")
        name = self._variable.get()
        w, h, hc, vc, limit = canvas.meta()
        canvas.collect("d0", canvas.create_text(hc, h * .1, anchor="n", text=name, font=self._font[0]))
        users = list_users()
        block = w / (len(users) + 1)
        for i in range(len(users)):
            u = users[i]
            canvas.collect(f"d{u.name()}", canvas.create_text(block * (i + 1), h * .9, anchor="s", text=u.name(),
                                                              font=self._font[1],
                                                              fill="green" if u.name() == name else self._text_color))

    @_override
    def raw_renderer(self, canvas: _CanvasBased) -> None:
        canvas.clear()
        canvas.draw_fg(self._fg_color, self._hover_color, self._corner_radius)
        self.dynamic_renderer(canvas)


_user_window_index: int = 0


def show_or_hide_user_window(context_manager: _ContextManager, var_user: _StringVar) -> None:
    global _user_window_index
    if _user_window_index > 0:
        context_manager.window(_user_window_index - 1).hide()
        _user_window_index = -_user_window_index
    elif _user_window_index < 0:
        context_manager.window(-_user_window_index - 1).show()
        _user_window_index = -_user_window_index
    else:
        root_window = context_manager.window()
        rd = root_window.runtime_data()
        width = int(root_window.width() * .6)
        height = int(root_window.height() * .6)
        w = _Window(width, height, root_window.refresh_rate(), rd,
                    display=root_window.screen_index())
        window_index = context_manager.add_window(w)
        _user_window_index = window_index + 1
        context_manager["user_chooser"] = UserChooser(w.root(), width=width, height=height, variable=var_user)
        context_manager.layout([["user_chooser"]], 0, window_index)
