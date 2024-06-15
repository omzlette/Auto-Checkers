#!/usr/bin/python3
import time
import serial

def initial_serial(port="COM6", baudrate=115200):
    try:
        ser = serial.Serial(port=port,
                            baudrate=baudrate,
                            parity=serial.PARITY_NONE,
                            stopbits=serial.STOPBITS_ONE,
                            bytesize=serial.EIGHTBITS,
                            timeout=1)
        return ser
    except Exception as e:
        print(e)
        return None
    
def close_serial(serial_port):
    if serial_port and serial_port.is_open:
        serial_port.close()
        return True
    
def main():
    experiment = initial_serial()
    
    if experiment is None:
        print("Serial port not found")
        return
    
    TxBuffer = "~/miniforge3/envs/checkers/bin/python ~/Auto-Checkers/arduino/uart-jetson.py\r"
    print(f"Sending: {TxBuffer.strip()}")
    experiment.write(TxBuffer.encode('utf-8'))
    time.sleep(3)

    while True:
        try:
            TxBuffer = "Hello from Python\n"
            print(f"Sending: {TxBuffer.strip()}")
            experiment.write(TxBuffer.encode('utf-8'))
            time.sleep(1)

            if experiment.in_waiting > 0:
                RxBuffer = experiment.readall().decode('utf-8').strip()
                if RxBuffer:
                    lines = RxBuffer.split('\n')
                    last_line = lines[-1]
                    print(f'Received: {RxBuffer}')
                    print(f"Received (Last Line): {last_line}\n")

            time.sleep(1)
        except KeyboardInterrupt:
            TxBuffer = '\x03\x03'
            print(f"Sending: {TxBuffer}")
            experiment.write('\x03'.encode('ascii'))
            break
    
    close_serial(experiment)

if __name__ == "__main__":
    main()