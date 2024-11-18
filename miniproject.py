import serial
import time
arduino_port="COM3"
baud=9600
ser = serial.Serial(arduino_port,baud)

def read_smoke_value():
    ser.write(b'1')
    value = ser.readline().decode('utf-8').strip()
    print(f"Soil Moisture: {value}")
    line = ser.readline().decode('utf-8').strip()
    print(line)


while True:
    read_smoke_value()
    time.sleep(2)