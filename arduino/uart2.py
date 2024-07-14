import serial
import struct

ser = serial.Serial('COM4', 115200)

logEncoder = open('logEncoder.txt', 'w', 1)
logEncoder.write('Raw Angle, Time, Match Flag, Started\n')

while True:
    dataEncoder = ser.read(10)
    if len(dataEncoder) == 10:
        rawAngle, Time2, matcher, startedStatus = struct.unpack('iiBB', dataEncoder)
        logEncoder.write(f"{rawAngle}, {Time2}, {matcher}, {startedStatus}\n")