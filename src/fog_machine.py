import pygame
import serial
import serial.tools.list_ports
import sys
import time

class FogMachine():
    def __init__(self, port : str = None):
        self.on_bytes =  b'\xa0\x01\x01\xa2'  # A0 01 01 A2
        self.off_bytes = b'\xa0\x01\x00\xa1'  # A0 01 00 A1
        self.port_name : str = port
        self.serial : serial.Serial = None
        if port is not None:
            self.serial = serial.Serial(port,9600) # open serial port

    def closeRelay(self, on : bool):
        if isinstance(on, bool) and self.serial is not None:
            delay = 0.02
            bytes_written = 0
            while bytes_written != 4:
                try:
                    if not self.serial.is_open:
                        self.serial.open()
                        time.sleep(delay)
                    if on:
                        #print("Turning on")
                        bytes_written = self.serial.write(self.on_bytes)
                        time.sleep(delay)
                    else:
                        #print('Turning off')
                        bytes_written = self.serial.write(self.off_bytes)
                        time.sleep(delay)
                    self.serial.close()
                except Exception as e:
                    bytes_written = 0
                    print(f'Got exception: {e}')

    def produceSmoke(self, dur_ms : int = 1000):
        self.closeRelay(True)
        time.sleep(dur_ms / 1000)
        self.closeRelay(False)
        

def find_ch340_device() -> str:
    """
    Finds and prints information about connected CH340 devices.
    """
    ch340_ports = []
    ports = serial.tools.list_ports.comports()
    #print(ports)
    if ports is None:
        print('No comports found')
        return None

    for port in ports:
        print(port.description)
        # CH340 devices often have "CH340" in their description or manufacturer string.
        # You might need to adjust this check based on your specific device.
        if "USB Serial" in port.description: # or "CH340" in port.manufacturer:
            print(f"  Port: {port.device}")
            print(f"  Description: {port.description}")
            print(f"  Manufacturer: {port.manufacturer}")
            print(f"  Hardware ID: {port.hwid}\n")
            return port.device

    return None

if __name__ == "__main__":
    port_name = find_ch340_device()
    if port_name is not None:
        fg = FogMachine(port_name)
        fg.closeRelay(True)
        time.sleep(1)
        fg.closeRelay(False)