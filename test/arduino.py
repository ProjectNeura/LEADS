from leads_arduino import ArduinoNano

controller = ArduinoNano()
controller.initialize()
print(controller.read())
