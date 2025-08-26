import machine

HOT = machine.Pin(3, machine.Pin.OUT)
COLD = machine.Pin(5, machine.Pin.OUT)

dryhop1 = machine.Pin(10, machine.Pin.OUT)
dryhop1.value(0)
