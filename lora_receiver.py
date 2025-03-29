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

# Set frequency to 915 MHz
print("Set frequency to 915 MHz")
lora.setFrequency(868000000)

# Set RX gain. RX gain options are power saving gain or boosted gain
print("Set RX gain to power saving gain")
lora.setRxGain(lora.RX_GAIN_POWER_SAVING, lora.RX_GAIN_AUTO)  # AGC on, Power saving gain

# Configure modulation parameters
print("Set modulation parameters:\n\tSpreading factor = 7\n\tBandwidth = 125 kHz\n\tCoding rate = 4/5")
lora.setSpreadingFactor(7)
lora.setBandwidth(125000)
lora.setCodeRate(5)

# Configure packet parameters
print("Set packet parameters:\n\tExplicit header type\n\tPreamble length = 12\n\tPayload Length = 15\n\tCRC on")
lora.setHeaderType(lora.HEADER_EXPLICIT)
lora.setPreambleLength(12)
lora.setPayloadLength(15)
lora.setCrcEnable(True)

# Set synchronize word for public network (0x34)
print("Set synchronize word to 0x34")
lora.setSyncWord(0x34)

print("\n-- LoRa Receiver --\n")

# Receive message continuously
while True:
    # Request for receiving new LoRa packet
    lora.request()
    # Wait for incoming LoRa packet
    lora.wait()

    # Put received packet to message and counter variable
    message = ""
    while lora.available() > 1:
        message += chr(lora.read())
    counter = lora.read()

    # Print received message and counter
    print(f"{message}  {counter}")

    # Print packet/signal status including RSSI, SNR, and signalRSSI
    print("Packet status: RSSI = {0:0.2f} dBm | SNR = {1:0.2f} dB".format(lora.packetRssi(), lora.snr()))

    # Show received status in case CRC or header error occur
    status = lora.status()
    if status == lora.STATUS_CRC_ERR:
        print("CRC error")
    elif status == lora.STATUS_HEADER_ERR:
        print("Packet header error")

