from dearpygui import dearpygui as _dpg


def initialize():
    _dpg.create_context()
    _dpg.create_viewport()
    _dpg.setup_dearpygui()
    with _dpg.window(label="LEADS", no_title_bar=True, no_scrollbar=True, menubar=False):
        _dpg.add_text("TEST")


if __name__ == '__main__':
    _dpg.create_context()
    _dpg.create_viewport()
    _dpg.setup_dearpygui()
    with _dpg.window(label="LEADS", no_title_bar=True, no_scrollbar=True, menubar=False):
        _dpg.add_text("TEST")
    _dpg.setup_dearpygui()
    _dpg.show_viewport()
    _dpg.start_dearpygui()
