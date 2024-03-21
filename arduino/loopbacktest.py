import serial

ser = serial.Serial('/dev/ttyTHS1', 9600)
ser.write(b'Hello World')
ser.flush()

print(ser.read_all())