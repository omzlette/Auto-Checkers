import serial
import struct

ser = serial.Serial('COM4', 115200)
logEncoder = open('logEncoder_run_NOLOAD.txt', 'w', 1)
logEncoder.write('Raw Angle, Time\n')

while True:
    dataEncoder = ser.read(8)
    if len(dataEncoder) == 8:
        rawAngle, Time2 = struct.unpack('ii', dataEncoder)
        logEncoder.write(f"{rawAngle}, {Time2}\n")