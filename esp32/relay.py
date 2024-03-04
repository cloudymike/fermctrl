import machine

HOT = machine.Pin(19, machine.Pin.OUT)
COLD = machine.Pin(23, machine.Pin.OUT)

dryhop1 = machine.Pin(33, machine.Pin.OUT)
dryhop1.value(0)
