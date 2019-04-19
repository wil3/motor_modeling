import serial
import struct
import csv


test = ser = serial.Serial('COM1', baudrate=2000000)
data = []

try:
	while True:
		'''
		one = ord(test.read())
		two = ord(test.read())
		three = ord(test.read())
		four = ord(test.read())
		'''

		#line = test.read(4) #binascii.hexlify(test.read(4))
		line = test.readline()#.rstrip()
		print(line)
		'''
		if (len(line) == 4) :
			line = struct.unpack('<f', line)[0]
			#print(one, ' | ', two, ' | ', three, ' | ', four)
			print(line)
			#data.append(str(line))
		'''

except KeyboardInterrupt:
	with open('rpmTest.csv', "a", newline='') as f:
		writer = csv.writer(f)
		for z in data:
			if (z != None):
				writer.writerow(z)
