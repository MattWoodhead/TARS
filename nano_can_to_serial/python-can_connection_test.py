# -*- coding: utf-8 -*-
"""
Created on Sun Apr 10 23:16:45 2022

Adapted from: https://github.com/hardbyte/python-can/blob/develop/examples/serial_com.py
"""

import time
import threading
import can

PREVIOUS_TIMESTAMP = 0
YAW = 0
PITCH = 0
ROLL = 0
SWAY = 0
SURGE = 0
HEAVE = 0
CAN_UPDATE = False

def receive(bus, stop_event):
    """The loop for receiving."""
    print("Start receiving messages")

    global YAW  # TODO - globals are horrid
    global PITCH
    global ROLL
    global SWAY
    global SURGE
    global HEAVE
    global PREVIOUS_TIMESTAMP
    global CAN_UPDATE

    while not stop_event.is_set():
        rx_msg = bus.recv(1)
        if rx_msg is not None:
            #print(f"rx: {rx_msg}")
            if rx_msg.arbitration_id == 0x0cf029e2:  # PITCH AND ROLL BROADCAST DATA
                PITCH = rx_msg.data[0] + (rx_msg.data[1] << 8) + (rx_msg.data[2] << 16)
                ROLL = rx_msg.data[3] + (rx_msg.data[4] << 8) + (rx_msg.data[5] << 16)
                PITCH = (PITCH - 8192000)/32768
                ROLL = (ROLL - 8192000)/32768
            elif rx_msg.arbitration_id == 0x0Cf02ae2:  # ANGULAR RATE BROADCAST DATA
                pitch_rate = ((rx_msg.data[0] + (rx_msg.data[1] << 8)) - 32000)/128
                roll_rate = ((rx_msg.data[2] + (rx_msg.data[3] << 8)) - 32000)/128
                yaw_rate = ((rx_msg.data[4] + (rx_msg.data[5] << 8)) - 32000)/128
                new_timestamp = rx_msg.timestamp
                if PREVIOUS_TIMESTAMP > 0:
                    YAW = YAW + yaw_rate*(new_timestamp - PREVIOUS_TIMESTAMP)
                PREVIOUS_TIMESTAMP = new_timestamp
            elif rx_msg.arbitration_id == 0x08f02de2:  # ACCELERATION BROADCAST DATA
                SWAY = ((rx_msg.data[0] + (rx_msg.data[1] << 8)) - 32000)/100
                SURGE = ((rx_msg.data[2] + (rx_msg.data[3] << 8)) - 32000)/100
                HEAVE = ((rx_msg.data[4] + (rx_msg.data[5] << 8)) - 32000)/100
                print(f"{SWAY}, {SURGE}, {HEAVE}")
            else:
                print(rx_msg.arbitration_id)


            print(f"{PITCH}, {ROLL}, {YAW}")
    print("Stopped receiving messages")


def main():
    """Controls the sender and receiver."""
    with can.interface.Bus(interface="serial", channel="COM4", baudrate=115200) as client:

        # Thread for sending and receiving messages
        stop_event = threading.Event()
        t_receive = threading.Thread(target=receive, args=(client, stop_event))
        t_receive.start()

        try:
            while True:
                time.sleep(0)  # yield
        except KeyboardInterrupt:
            pass  # exit normally

        stop_event.set()
        time.sleep(0.5)


    print("Stopped script")


if __name__ == "__main__":
    main()
