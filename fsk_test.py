import time
from LoRaRF import SX127x

# Initialize radio module
radio = SX127x()

# Set SPI bus configuration (SPI bus 0, chip select 0)
radio.setSpi(0, 0)

# Set GPIO pins: NSS (CS), RESET, and DIO0 (IRQ)
radio.setPins(8, 22, 25)  # NSS=8 (GPIO8/CE0), RESET=22, DIO0=25

REG_FIFO          = 0x00
REG_OPMODE        = 0x01
REG_FRFMSB        = 0x06
REG_PACONFIG      = 0x09
REG_LNAVALUE      = 0x0C
REG_RXCONFIG      = 0x0D
REG_RSSITHRES     = 0x10
REG_AFCFEI        = 0x1A
REG_AFCMSB        = 0x1B
REG_AFCLSB        = 0x1C
REG_FEIMSB        = 0x1D
REG_FEILSB        = 0x1E
REG_RSSIVALUE     = 0x11
REG_IRQFLAGS1     = 0x3E
REG_IRQFLAGS2     = 0x3F
REG_DIOMAPPING1   = 0x40
REG_DIOMAPPING2   = 0x41
REG_SYNCVALUE1    = 0x28
REG_SYNCVALUE3    = 0x2A
REG_NODEADDR      = 0x33
REG_BCASTADDR     = 0x34
REG_PADAC         = 0x4D

MODE_SLEEP        = 0x00
MODE_STANDBY      = 0x01
MODE_FSTX         = 0x02
MODE_TRANSMIT     = 0x03
MODE_FSRX         = 0x04
MODE_RECEIVE      = 0x05

IRQ2_PAYLOADREADY = 1 << 2
IRQ1_RXREADY = 1 << 6
IRQ1_SYNCADDMATCH = 1 << 0
IRQ1_VALIDPREAMBLE = 1 << 1
CRC_OK = 1 << 1
FIFO_FULL = 1 << 7
FIFO_OVERRUN = 1 << 4

frequency = 866000000
syncwords = [0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF]
preamble = 5  # 5 bytes = 40 bits
bitrate = 250000
fdev = 125000  # 125 kHz
rx_bw = 250000

# Reset RF module by setting resetPin to LOW and begin SPI communication
radio.reset()
version = radio.readRegister(radio.REG_VERSION)
if version == 0x12 or version == 0x22:
    print("Resetting module")
else:
    print("Something wrong, can't reset FSK radio")

def set_mode(mode):
    radio.writeRegister(REG_OPMODE, 0x00)  # Force Sleep mode
    time.sleep(0.01)
    radio.writeRegister(REG_OPMODE, mode)
    time.sleep(0.01)  # <-- Add this delay
    read_mode = radio.readRegister(REG_OPMODE)
    print(f"REG_OP_MODE = {hex(read_mode)}")

def set_frequency(frequency):
    print("\n--Frequency--")
    frf = int((frequency << 19) / 32000000)
    radio.writeRegister(radio.REG_FRF_MSB, (frf >> 16) & 0xFF)
    radio.writeRegister(radio.REG_FRF_MID, (frf >> 8) & 0xFF)
    radio.writeRegister(radio.REG_FRF_LSB, frf & 0xFF)
    print(f"Calculated FRF = {frf}")
    print(f"Set frequency to {frequency / 1000000} MHz")

    # Read them back again for verification
    frf_msb = radio.readRegister(radio.REG_FRF_MSB)
    frf_mid = radio.readRegister(radio.REG_FRF_MID)
    frf_lsb = radio.readRegister(radio.REG_FRF_LSB)
    calculated_frf = (frf_msb << 16) | (frf_mid << 8) | frf_lsb
    print(f"Frequency Registers: MSB={hex(frf_msb)} MID={hex(frf_mid)} LSB={hex(frf_lsb)}")
    print(f"Read-back Calculated FRF = {calculated_frf}")

def set_syncWords(syncwords):
    print("\n--Sync Words--")
    
    # Set SyncConfig:
    # Bit 7-6: AutoRestartRxMode = 00 (Off)
    # Bit 5: PreamblePolarity = 0 (0xAA)
    # Bit 4: SyncOn = 1 (enable sync word detection)
    # Bits 2-0: SyncSize = len(syncwords) - 1
    sync_config = 0b10000000 | ((len(syncwords) - 1) & 0x07)  # Set SyncSize with bits 2-0
    radio.writeRegister(0x27, sync_config)
    print(f"Set RegSyncConfig = {hex(sync_config)}")

    # Write sync word bytes into RegSyncValue1 to RegSyncValue8 (0x28 to 0x2F)
    for i, byte in enumerate(syncwords):
        reg_addr = 0x28 + i
        radio.writeRegister(reg_addr, byte)
        print(f"RegSyncValue{i+1} (0x{reg_addr:02X}) = {hex(byte)}")


def set_preambleLength(preamble):
    print("\n--Set Preamble Length--")
    radio.writeRegister(0x25, (preamble >> 8) & 0xFF)  # RegPreambleMsb
    radio.writeRegister(0x26, preamble & 0xFF)         # RegPreambleLsb

    preamble_msb = radio.readRegister(0x25)
    preamble_lsb = radio.readRegister(0x26)
    actual_preamble = (preamble_msb << 8) | preamble_lsb
    print(f"Preamble Length Set: {actual_preamble} bytes ({actual_preamble * 8} bits)")

def set_bitrate(bitrate):
    print("\n--Bitrate--")
    total = 32000000 / bitrate
    bitrate_int = int(total)
    bitrate_frac = int(round((total - bitrate_int) * 16))

    msb = (bitrate_int >> 8) & 0xFF
    lsb = bitrate_int & 0xFF

    radio.writeRegister(0x02, msb)       # RegBitrateMsb
    radio.writeRegister(0x03, lsb)       # RegBitrateLsb
    radio.writeRegister(0x5D, bitrate_frac)  # RegBitrateFrac

    print(f"Target Bitrate: {bitrate} bps")
    print(f"RegBitrateMsb (0x02) = {hex(msb)}")
    print(f"RegBitrateLsb (0x03) = {hex(lsb)}")
    print(f"RegBitrateFrac (0x5D) = {hex(bitrate_frac)}")

def set_Freqdev(fdev):
    print("\n--Frequency Deviation--")
    fstep = 32000000 / (2 ** 19)  # ≈ 61.035 Hz
    fdev_value = int(fdev / fstep)  # ≈ 2049

    radio.writeRegister(0x04, (fdev_value >> 8) & 0xFF)  # RegFdevMsb = 0x08
    radio.writeRegister(0x05, fdev_value & 0xFF)         # RegFdevLsb = 0x01

    # Optional: verify
    msb = radio.readRegister(0x04)
    lsb = radio.readRegister(0x05)
    actual_fdev = ((msb << 8) | lsb) * fstep
    print(f"Set Fdev: {actual_fdev:.2f} Hz (RegFdevMsb=0x{msb:02X}, RegFdevLsb=0x{lsb:02X})")

def set_RxBandwidth(target_bw):
    print("\n--RX Bandwidth--")
    FXOSC = 32_000_000
    best_error = float('inf')
    best_mant_exp = (None, None)

    # RxBwMant values: code -> actual
    mant_map = {
        0b00: 16,
        0b01: 20,
        0b10: 24,
    }

    # Try all valid combinations of mantissa and exponent
    for mant_code, mant_val in mant_map.items():
        for exp in range(8):  # RxBwExp is 3 bits
            bw = FXOSC / (mant_val * (2 ** (exp + 2)))
            error = abs(target_bw - bw)
            if error < best_error:
                best_error = error
                best_mant_exp = (mant_code, exp)
            if error == 0:
                break

    mant_code, exp = best_mant_exp
    reg_value = (mant_code << 3) | exp

    radio.writeRegister(0x12, reg_value)  # RegRxBw

    print(f"Target RX BW: {target_bw:.1f} Hz")
    print(f"Set RegRxBw = 0x{reg_value:02X} (Mant: {mant_map[mant_code]}, Exp: {exp})")
    actual_bw = FXOSC / (mant_map[mant_code] * (2 ** (exp + 2)))
    print(f"Actual RX BW: {actual_bw:.1f} Hz")

def check_packet():
    irq2 = radio.readRegister(REG_IRQFLAGS2)

    irq1 = radio.readRegister(REG_IRQFLAGS1)

    if irq1 & IRQ1_SYNCADDMATCH:
        print("Sync address match!")
    
    if irq1 & IRQ1_VALIDPREAMBLE:
        print("Valid preamble!")

    if irq2 & CRC_OK:
        print("CRC OK!")


def setup_fsk_rx():
    print("\n--Setting up FSK RX--")
    set_mode(MODE_STANDBY) 

    radio.writeRegister(REG_DIOMAPPING1, 0b00000000)  # DIO0 = PayloadReady

    set_mode(MODE_RECEIVE) 

    while True:
        irq1 = radio.readRegister(REG_IRQFLAGS1)

        if irq1 & IRQ1_RXREADY:
            print("RX Ready!")
            break

        time.sleep(0.01)

    print("Receiver started.\n")

set_mode(MODE_SLEEP)
set_frequency(frequency)
set_syncWords(syncwords)
set_preambleLength(preamble)
set_bitrate(bitrate)
set_Freqdev(fdev)
set_RxBandwidth(rx_bw)
setup_fsk_rx()

while True:

    check_packet()

    irq2 = radio.readRegister(REG_IRQFLAGS2)

    if irq2 & FIFO_FULL:
          print("FIFO full!")
    
    if irq2 & FIFO_OVERRUN:
          print("FIFO overrun!")

    if irq2 & IRQ2_PAYLOADREADY:
        print("PayloadReady detected.")

        size = radio.readRegister(REG_FIFO)
        rxBuffer = [0] * size

        for i in range(size):
            rxBuffer[i] = radio.readRegister(REG_FIFO)

        print("Received: ", end='')
        for i in range(size):
            print(chr(rxBuffer[i]), end='') 
        
        print()

        # Clear FIFO / IRQ flags
        radio.writeRegister(REG_IRQFLAGS1, 0xFF)
        radio.writeRegister(REG_IRQFLAGS2, 0xFF)
        set_mode(MODE_STANDBY)
        set_mode(MODE_RECEIVE)

    time.sleep(0.01)