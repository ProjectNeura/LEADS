import dearpygui.dearpygui as dpg


dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

with dpg.window(label="LEADS", no_title_bar=True, no_scrollbar=True, menubar=False, no_close=True):
    dpg.add_text("TEST", tag="speed")

dpg.show_viewport()

i = 0
while dpg.is_dearpygui_running():
    i += 1
    dpg.set_value("speed", str(i))
    dpg.render_dearpygui_frame()

dpg.destroy_context()
