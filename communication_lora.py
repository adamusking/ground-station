import time
import threading
import queue
import sys
from LoRaRF import SX127x


lora = SX127x()
lora.setSpi(0, 0)
lora.setPins(8, 22, 25)  # NSS=8 (GPIO8/CE0), RESET=22, DIO0=25

print("Begin LoRa radio")
if not lora.begin():
    raise Exception("Something wrong, can't begin LoRa radio")

print("Set frequency to 866 MHz")
lora.setFrequency(866000000)

print("Set RX gain to power saving gain")
lora.setRxGain(lora.RX_GAIN_POWER_SAVING, lora.RX_GAIN_AUTO)  # AGC on, Power saving gain

print("Set modulation parameters:\n\tSpreading factor = 7\n\tBandwidth = 125 kHz\n\tCoding rate = 4/5")
lora.setSpreadingFactor(7)
lora.setBandwidth(125000)
lora.setCodeRate(5)

print("Set packet parameters:\n\tExplicit header type\n\tPreamble length = 12\n\tPayload Length = variable (automatic)\n\tCRC on")
lora.setHeaderType(lora.HEADER_EXPLICIT)
lora.setPreambleLength(12)
lora.setCrcEnable(True)

print("Set synchronize word to 0xA5")
lora.setSyncWord(0xA5)

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
    while True:
        user_input = sys.stdin.readline().strip()
        input_queue.put(user_input)

# Start the input thread
threading.Thread(target=read_input, daemon=True).start()

print("LoRa Ground Station Started...")

while True:
    packet_id = "UNKNOWN"  # Default in case no ID is found
    command = ""

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
    
    lora.request()
    lora.wait()

    message = ""
    while lora.available() > 1:
        message += chr(lora.read())
    counter = lora.read()

    print(f"{message}  {counter}")
    print("Packet status: RSSI = {0:0.2f} dBm | SNR = {1:0.2f} dB".format(lora.packetRssi(), lora.snr()))
    
    status = lora.status()
    if status == lora.STATUS_CRC_ERR:
        print("CRC error")
    elif status == lora.STATUS_HEADER_ERR:
        print("Packet header error")

    if message.startswith("ID"):
        parts = message.split(",")  # Split by comma
        if len(parts) > 0:
            packet_id = parts[0].split(":")[1]  # Extract ID value
    

            

    ack = f"ACK{packet_id}, {command}"
    ack_list = [ord(c) for c in ack]
    counter1 = 0

    lora.beginPacket()
    lora.write(ack_list, len(ack_list))
    lora.write([counter1], 1)
    lora.endPacket()

    print(f"Sending ACK: {ack}  {counter1}")

    lora.wait()
    print("Transmit time: {0:0.2f} ms | Data rate: {1:0.2f} byte/s".format(lora.transmitTime(), lora.dataRate()))
    
    counter = (counter + 1) % 256

    '''
    if mode != prev_mode:
        if mode:
            print(f"Switching to LoRa...")
            lora.set_mode_rx()  # LoRa mode (default)
        else:
            print(f"Switching to FSK...")
            lora.write_register(0x2C, 0x10)  # Enable CRC for FSK
            lora.write_register(0x01, 0x00)  # Put radio in standby
            lora.write_register(0x01, 0x20)  # Set to FSK mode
            lora.set_mode_rx()  # Back to RX
        
        prev_mode = mode  # Update the last mode
    '''