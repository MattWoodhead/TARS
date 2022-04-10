# -*- coding: utf-8 -*-
"""
Created on Sun Apr 10 23:16:45 2022
Adapted from: https://github.com/hardbyte/python-can/blob/develop/examples/serial_com.py
"""

import time
import threading
import can


def receive(bus, stop_event):
    """The loop for receiving."""
    print("Start receiving messages")
    while not stop_event.is_set():
        rx_msg = bus.recv(1)
        if rx_msg is not None:
            print(f"rx: {rx_msg}")
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
