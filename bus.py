import serial
import time

MAXTRIES = 3

def swapbyte(b):
	return int("0b"+"{0:08b}".format(b)[::-1], 2)

class Bus:
	def __init__(self, tty):
		self.initialized = False
		self.tty = tty
		try:
			self.port = serial.Serial(port=self.tty,
					baudrate=19200,
					bytesize=serial.EIGHTBITS,
					parity=serial.PARITY_NONE,
					stopbits=serial.STOPBITS_ONE, 
					timeout=0)

		except serial.SerialException:
			self.port = None
			print("Unable to Connect to serial port %s" % tty)
			return

		self.initialized = True

	def close(self):
		self.port.close()

	def sendRecv(self, address, outbuf, nbytes, swap=False):
		if not self.initialized:
			return None, 0

		nb = self.port.write(bytes([address]))
		if nb != 1:
			print("expected 1 byte written, got %d" % nb)

		# print("before")
		# for b in outbuf:
		# 	print("{0:08b}".format(b))
		if swap:
			outbuf = [swapbyte(x) for x in outbuf]
		# print("after")
		# for b in outbuf:
		# 	print("{0:08b}".format(b))

		nb = self.port.write(bytes(outbuf))
		if nb != nbytes:
			print("expected %d byte(s) written, got %d" % (nbytes, nb))

		tries = 0
		inbuf = []
		while tries < MAXTRIES and len(inbuf) < nbytes:
			b = self.port.read(1)
			if len(b) == 0:
				tries += 1
				time.sleep(0.001)
			else:
				tries = 0
				inbuf.append(b)
				
		if len(inbuf) != nbytes:
			print("incomplete read.  Expecting %d characters, got %d" % (nbytes, len(inbuf)))
			return None, 0

		return inbuf, nbytes


		