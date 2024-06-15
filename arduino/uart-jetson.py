import time
import serial

def initial_serial(port="/dev/ttyGS0", baudrate=115200):
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

    while True:
        try:
            if experiment.in_waiting > 0:
                RxBuffer = experiment.readline().decode('utf-8').strip()
                print(f'Received: {RxBuffer}')

                if RxBuffer == 'exit':
                    break

                time.sleep(1)
                TxBuffer = "echooo\n"
                experiment.write(TxBuffer.encode('utf-8'))

            time.sleep(1)
            

        except KeyboardInterrupt:
            break
    
    close_serial(experiment)

if __name__ == "__main__":
    main()