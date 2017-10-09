#!/usr/bin/env /usr/bin/python
from bluepy.btle import Scanner, DefaultDelegate
import thread
import Queue
import serial
import pynmea2

longitude=0
latitude=0
gpsdev="/dev/ttyUSB0"

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            connect=""
            if dev.connectable:
                connect="connectable";
            response=(dev.getValueText(9), dev.addr, connect)
            blequeue.put(response)

def scanble():
    scanner=Scanner(1).withDelegate(ScanDelegate())
    devices=scanner.scan(0)

def readgps():
    while True:
        with serial.Serial(gpsdev) as gpsserial:
            line=gpsserial.readline()
            try: 
                sentence=pynmea2.parse(line)
                if sentence.latitude > 0 and sentence.longitude >0:
                    gpsqueue.put((latitude, longitude))
            except:
                pass

# Queue for transferring data from BLE
blequeue=Queue.Queue(maxsize=0)
gpsqueue=Queue.Queue(maxsize=0)
thread.start_new_thread( readgps, () )
thread.start_new_thread( scanble, () )
while True:
    if not gpsqueue.empty():
        coords=gpsqueue.get()
        latitude=coords[0]
        longitude=coords[1]
    if not blequeue.empty():
        details=blequeue.get()
        print "Discovered device", details[0], details[1], details[2], latitude, longitude
