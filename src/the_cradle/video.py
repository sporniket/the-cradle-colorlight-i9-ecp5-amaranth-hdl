"""
---
(c) 2022,2023 David SPORN
---
This is part of Sporniket's "The Cradle for MuseLab's Colorlight i9" project.

Sporniket's "The Cradle for MuseLab's Colorlight i9" project is free software: you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your option)
any later version.

Sporniket's "The Cradle for MuseLab's Colorlight i9" project is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE.

See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with Sporniket's "The Cradle for MuseLab's Colorlight i9" project.
If not, see <https://www.gnu.org/licenses/>. 
---
"""


### builtin deps
from typing import List  # , Dict, Tuple, Optional

### amaranth -- main deps
from amaranth import *
from amaranth.build import Platform


red_content = [0xFF if i % 3 == 0 else 0 for i in range(0, 1024)] + [
    0xFF if i % 3 == 0 else 0 for i in range(0, 1024)
]
green_content = [0xFF if i % 3 == 1 else 0 for i in range(0, 1024)] + [
    0xFF if i % 3 == 1 else 0 for i in range(0, 1024)
]
blue_content = [0xFF if i % 3 == 2 else 0 for i in range(0, 1024)] + [
    0xFF if i % 3 == 2 else 0 for i in range(0, 1024)
]


class VideoLineBuffer(Elaboratable):
    WIDTH_OF_ADDRESS = 11
    DEPTH_OF_MEMORY = 2**WIDTH_OF_ADDRESS

    def __init__(self, pixelDomain: str, memoryDomain: str):
        self.domainOfPixel = pixelDomain
        self.domainOfMemory = memoryDomain

        # TODO an interface
        self.dataIn = Signal(24)
        self.dataOut = Signal(24)
        self.dataStrobe = Signal()
        self.switchStrobe = Signal()
        self.switchAcknowledge = Signal()
        self.hsync = Signal()
        self.videoDisplayEnable = Signal()

        # memory array
        self.redBuffer = Memory(8, DEPTH_OF_MEMORY, red_content)
        self.greenBuffer = Memory(8, DEPTH_OF_MEMORY, green_content)
        self.blueBuffer = Memory(8, DEPTH_OF_MEMORY, blue_content)

        # buffer state 
        # displayLine
        # -- 0 -> read line 0, write line 1
        # -- 1 -> write line 0, read line 1
        self.displayLine = Signal() 

    def elaborate(self, p: Platform) -> Module:
        m = Module()

        ### ===-===-===-===-===-===-===-===-===-===-===-===-===-===-===-===-===
        # Registering submodules that can be instancied in advance
        # -- from self
        m.submodules.redBuffer = redBuffer = self.redBuffer
        m.submodules.greenBuffer = greenBuffer  = self.greenBuffer
        m.submodules.blueBuffer = blueBuffer = self.blueBuffer

        # -- I need a counter for scanning memory for output
        m.submodules.vidCounter = vidCounter = DomainRenamer(self.domainOfPixel)(ResetInserter(hsync)(EnableInserter(vde)(RippleCounter(10))))

        # I need a counter for scanning memory for input
        m.submodules.writeCounter = writeCounter = DomainRenamer(self.domainOfMemory)(ResetInserter(switchStrobe)(EnableInserter(dataStrobe)(RippleCounter(10))))

        ### ===-===-===-===-===-===-===-===-===-===-===-===-===-===-===-===-===
        # wiring dataOut
        addrRead = Signal(WIDTH_OF_ADDRESS)
        redReader = redBuffer.read_port(self.domainOfPixel)
        greenReader = greenBuffer.read_port(self.domainOfPixel)
        blueReader = blueBuffer.read_port(self.domainOfPixel)
        m.d.comb += [
            addrRead.eq(Cat(vidCounter.value, self.displayLine)),
            # always output value
            redReader.en.eq(Const(1)),
            greenReader.en.eq(Const(1)),
            blueReader.en.eq(Const(1)),
            self.dataOut.eq(Cat(blueReader.data, greenReader.data, redReader.data))
        ]

        ### ===-===-===-===-===-===-===-===-===-===-===-===-===-===-===-===-===
        # wiring dataIn
        addrWrite = Signal(WIDTH_OF_ADDRESS)
        redWriter = redBuffer.write_port(self.domainOfMemory)
        greenWriter = greenBuffer.write_port(self.domainOfMemory)
        blueWriter = blueBuffer.write_port(self.domainOfMemory)
        m.d.comb += [
            addrWrite.eq(Cat(vidCounter.value, ~self.displayLine)),
            redWriter.data.eq(self.dataIn[16:24]),
            greenWriter.data.eq(self.dataIn[8:16]),
            blueWriter.data.eq(self.dataIn[0:8]),
        ]

        ###
        # TODO I need some signals to manage switchStrobe 

        # TODO When receiving switchStrobe : 
        # * one should wait for the next leading edge of hsync
        # * Then the switch is done, and the switchAcknowledge is asserted ;
        # * Then switchStrobe is negated ;
        # * Then switchAcknowledge is negated.


        return m
