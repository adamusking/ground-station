from time import sleep
import time
import threading
import queue
import sys
from PySX127x.LoRa import LoRa
from PySX127x.board_config import BOARD

# Initialize board
BOARD.setup()

# Custom class to handle SX1276
class LoRaRadio(LoRa):
    def __init__(self, verbose=False):
        super().__init__(verbose)
        self.set_mode_rx()

    def on_rx_done(self):
        packet = self.read_payload(nocheck=True)
        print(f"Received: {packet.decode('utf-8', 'ignore')}")

        if packet.startswith("ID:"):
            parts = packet.split(",")  # Split by comma
            if len(parts) > 0:
                packet_id = parts[0].split(":")[1]  # Extract ID value

        # Store packet_id in the class instance (if needed)
        self.packet_id = packet_id

        self.set_mode_rx()

radio = LoRaRadio(verbose=False)
radio.set_mode_rx()

input_queue = queue.Queue()
duplicate = ""
mode = True  # true when LoRa
prev_mode = mode
command_map = {
    "lora": "LORA",
    "fsk": "FSK",
    "stand": "STAND",
    "wake": "WAKE",
}

def read_input():
    """Reads full-linende input in a separate thread and stores it in a queue."""
    while True:
        user_input = sys.stdin.readline().strip()
        input_queue.put(user_input)

# Start the input thread
threading.Thread(target=read_input, daemon=True).start()

print("LoRa Ground Station Started...")

while True:

    packet_id = "UNKNOWN"  # Default in case no ID is found

    if not input_queue.empty(): 
        command = input_queue.get().lower()
        print(f"Received command: {command}")

        if command in command_map and duplicate != command:
            duplicate = command
            command = command_map[command]  # Map input to uppercase form

            if command == "LORA":
                mode = True
            elif command == "FSK":
                mode = False

        else:
            print(f"Command {command} is invalid or has already been entered!")

            
        ack = f"ACK{radio.packet_id}, {command}"
        print(f"Sending ACK: {ack}")


        if mode != prev_mode:
            if mode:
                print(f"Switching to LoRa...")
                radio.set_mode_rx()  # LoRa mode (default)
            else:
                print(f"Switching to FSK...")
                radio.write_register(0x2C, 0x10)  # Enable CRC for FSK
                radio.write_register(0x01, 0x00)  # Put radio in standby
                radio.write_register(0x01, 0x20)  # Set to FSK mode
                radio.set_mode_rx()  # Back to RX
            
            prev_mode = mode  # Update the last mode
        
