import machine

HOTPIN = machine.Pin(3, machine.Pin.OUT)
COLD = machine.Pin(5, machine.Pin.OUT)

dryhop1 = machine.Pin(10, machine.Pin.OUT)
dryhop1.value(0)

class HOTSWAP:
	def __init__(self,inverted,pinnumber):
		self.hotpin = machine.Pin(pinnumber, machine.Pin.OUT)
		self.inverted=inverted

	def off():
		if inverted:
			self.hotpin.on()
		else:
			self.hotpin.off()

	def on():
		if inverted:
			self.hotpin.off()
		else:
			self.hotpin.on()


HOT=HOTSWAP(inverted=True,pinnumber=3)
