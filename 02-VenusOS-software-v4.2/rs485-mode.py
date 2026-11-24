#!/usr/bin/env python3
# Put /dev/ttySC3 (J402) into SC16IS752 auto RS-485 mode: RTSB (-> SP3485 DE/RE)
# HIGH while sending. Needed when the board config comes from config.txt (stock
# sc16is752-i2c overlay); the HAT EEPROM overlay already does this at boot.
# The setting stays in the kernel until reboot, so Venus' meter driver needs no change.
import fcntl, os, struct, sys
TIOCSRS485 = 0x542F
ENABLED, RTS_ON_SEND, RTS_AFTER_SEND, RX_DURING_TX = 1, 2, 4, 16
dev = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttySC3"
flags = ENABLED | RTS_AFTER_SEND | RX_DURING_TX   # RTS_AFTER_SEND = EFCR RTSINVER -> RTS high during TX
fd = os.open(dev, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
fcntl.ioctl(fd, TIOCSRS485, struct.pack("8I", flags, 0, 0, 0, 0, 0, 0, 0))
os.close(fd)
print(dev, "RS-485 auto direction on (DE high while sending)")
