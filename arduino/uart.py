import serial
import struct

ser = serial.Serial('COM5', 115200)
log = open('log.txt', 'w', 1)
log.write('Position, Velocity, Time, Started\n')

while True:
    data = ser.read(13)
    if len(data) == 13:
        currPos, vel, Time1, startedStatus = struct.unpack('ifiB', data)
        log.write(f"{currPos}, {vel}, {Time1}, {startedStatus}\n")