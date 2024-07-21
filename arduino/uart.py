import serial
import struct

ser = serial.Serial('COM5', 115200)
log = open('log_NOLOAD.txt', 'w', 1)
log.write('Position Generated, Velocity Generated, Raw Angle, Time\n')

while True:
    data = ser.read(16)
    if len(data) == 16:
        currPos, vel, rawAngle, Time = struct.unpack('ifii', data)
        log.write(f"{currPos}, {vel}, {rawAngle}, {Time}\n")