import serial
import struct

ser = serial.Serial('COM5', 115200)
log = open('log_run_NOLOAD.txt', 'w', 1)
log.write('Position Generated, Velocity Generated, Time\n')

while True:
    data = ser.read(12)
    if len(data) == 12:
        currPos, vel, Time = struct.unpack('ifi', data)
        log.write(f"{currPos}, {vel}, {Time}\n")