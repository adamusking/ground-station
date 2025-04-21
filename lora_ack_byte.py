import time
from LoRaRF import SX127x

# Initialize LoRa module
lora = SX127x()

# Set SPI bus configuration (SPI bus 0, chip select 0)
lora.setSpi(0, 0)

# Set GPIO pins: NSS (CS), RESET, and DIO0 (IRQ)
lora.setPins(8, 22, 25)  # NSS=8 (GPIO8/CE0), RESET=22, DIO0=25

print("Begin LoRa radio")
if not lora.begin():
    raise Exception("Something wrong, can't begin LoRa radio")

# Set frequency to 866 MHz
print("Set frequency to 866 MHz")
lora.setFrequency(866000000)

# Set RX gain. RX gain options are power saving gain or boosted gain
print("Set RX gain to power saving gain")
lora.setRxGain(lora.RX_GAIN_POWER_SAVING, lora.RX_GAIN_AUTO)  # AGC on, Power saving gain

print("Set TX power to +17 dBm")
lora.setTxPower(17, lora.TX_POWER_PA_BOOST)

# Configure modulation parameters
print("Set modulation parameters:\n\tSpreading factor = 7\n\tBandwidth = 125 kHz\n\tCoding rate = 4/5")
lora.setSpreadingFactor(7)
lora.setBandwidth(125000)
lora.setCodeRate(5)

# Configure packet parameters
print("Set packet parameters:\n\tExplicit header type\n\tPreamble length = 12\n\tPayload Length = 15\n\tCRC on")
lora.setHeaderType(lora.HEADER_EXPLICIT)
lora.setPreambleLength(12)
#lora.setPayloadLength(15)
lora.setCrcEnable(False)

# Set synchronize word (0xA5)
print("Set synchronize word to 0xA5")
lora.setSyncWord(0xA5)

print("\n-- LoRa Receiver --\n")

# Receive message continuously
while True:
    # Request for receiving new LoRa packet
    lora.request()
    # Wait for incoming LoRa packet
    lora.wait()

    print("\n\n---Receiving---")
    # Put received packet to message and counter variable
    """
    message = ""
    while lora.available() > 1:
        message += chr(lora.read())
    counter = lora.read()

    # Print received message and counter
    print(f"{message}  {counter}")
    """
    raw_data = []

# Read available bytes from the LoRa receiver
    while lora.available():
        raw_data.append(lora.read())

    print(f"Raw bytes: {raw_data}")

    # Example of decoding a uint8_t value from the raw data
    if len(raw_data) >= 1:
        packet_id = raw_data[0]  # Directly use the first byte as uint8_t
        print(f"Decoded uint8_t value: {packet_id}")

    # Print packet/signal status including RSSI, SNR, and signalRSSI
    print("Packet status: RSSI = {0:0.2f} dBm | SNR = {1:0.2f} dB".format(lora.packetRssi(), lora.snr()))
    
    #packet_id = int(message.split(',')[0].split(':')[1])
    


    # Show received status in case CRC or header error occur
    status = lora.status()
    if status == lora.STATUS_CRC_ERR:
        print("CRC error")
    elif status == lora.STATUS_HEADER_ERR:
        print("Packet header error")

    ack = f"ACK{packet_id}"
    ack_list = [ord(c) for c in ack]
    counter1 = 0
    
    print("\n\n---Transmitting---")
    lora.beginPacket()
    lora.write(ack_list, len(ack_list))
    lora.write([counter1], 1)
    lora.endPacket()
    
    print(f"Sending: {ack}  {counter1}")
    
    lora.wait()
    print("Transmit time: {0:0.2f} ms | Data rate: {1:0.2f} byte/s".format(lora.transmitTime(), lora.dataRate()))
    
   
    counter1 = (counter1 + 1) % 256

