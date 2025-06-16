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

### project deps
from ecp5 import Ehxplll
from .blinky import Blinky
from amaranth_stuff.modules import (
    MonoImpulse,
    Sequencer,
    RippleCounter,
    ShiftRegisterSendLsbFirst,
    DviTmdsEncoder,
)

# from .vid_settings_640x480_59Hz94 import (
# from .vid_settings_960x540_59Hz82 import (
# from .vid_settings_800x600_56Hz25 import (
# from .vid_settings_768x576_60Hz import (
# from .vid_settings_720x576_50Hz import (
from .vid_settings_960x540_50Hz import (
    mainPllParameters,
    mainPllClockMap,
    pixelSequence,
    scanlineSequence,
)

class TheCradle(Elaboratable):
    def __init__(self):
        pass

    def createClockDomain(
        self, m: Module, name: str, sourceClock, sourceReset=None
    ) -> ClockDomain:
        result = ClockDomain(name, local=True)
        m.d.comb += result.clk.eq(sourceClock)
        if sourceReset is not None:
            m.d.comb += result.rst.eq(sourceReset)
        m.domains += result
        return result

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        ## Setup blinky : shows that the fpga is running
        m.submodules.blinky = blinky = Blinky()

        ### Main pll and clocks
        m.submodules.mainPll = mainPll = Ehxplll(mainPllParameters)

        for dmn in mainPllClockMap:
            print(
                f"generating clock domain '{dmn}' using 'clkout{mainPllClockMap[dmn]}'..."
            )
            self.createClockDomain(
                m, dmn, mainPll.outputClockPorts()[mainPllClockMap[dmn]]
            )

        ### Pixel sequencer -> hsync clock
        m.submodules.pixelSequencer = pixelSequencer = DomainRenamer("pixel")(
            Sequencer(pixelSequence)
        )
        hsync = Signal()
        m.d.comb += hsync.eq(pixelSequencer.steps[0])
        henable = pixelSequencer.steps[2]

        self.createClockDomain(m, "hsync", hsync)

        ### Scanline sequencer -> vsync clock + video display enable
        m.submodules.scanlineSequencer = scanlineSequencer = DomainRenamer("hsync")(
            Sequencer(scanlineSequence)
        )
        vsync = Signal()
        m.d.comb += vsync.eq(scanlineSequencer.steps[0])
        venable = scanlineSequencer.steps[2]

        vde = Signal()
        m.d.comb += vde.eq(venable & henable)

        hsyncActive = Signal()  # Hsync pulse only for lines with displayable area
        m.d.comb += hsyncActive.eq(venable & hsync)

        m.submodules.vsyncPulseClock = vsyncPulseClock = DomainRenamer("pixel")(ResetInserter(~vsync)(MonoImpulse()))
        m.submodules.hsyncPulseClock = hsyncPulseClock = DomainRenamer("pixel")(ResetInserter(~hsync)(MonoImpulse()))

        ### The pixel source
        videoSource = Signal(
            24
        )  # v[0:8] = blue, v[8:16] = green, v[16:24] = red
        red, green, blue = Signal(8), Signal(8), Signal(8)
        m.d.comb += [
            blue.eq(videoSource[0:8]),
            green.eq(videoSource[8:16]),
            red.eq(videoSource[16:24]),
        ]

        videoSolidBlink = Signal(24)
        m.submodules.beat = beat = DomainRenamer("pixel")(EnableInserter(vsyncPulseClock.dataOut)(Sequencer([50, 50])))
        m.d.comb += videoSolidBlink.eq(Mux(beat.steps[0], 0x0055AA, 0xAA9955))

        m.submodules.redGradient = redGradient = DomainRenamer("pixel")(ResetInserter(~vde)(RippleCounter(8)))
        m.submodules.greenGradient = greenGradient = DomainRenamer("pixel")(ResetInserter(~venable)(EnableInserter(hsyncPulseClock.dataOut)(RippleCounter(8))))
        m.d.comb += videoSource.eq(Cat(videoSolidBlink[0:8], greenGradient.value, redGradient.value))

        ### The dvi link
        ctl0, ctl1, ctl2, ctl3 = Signal(), Signal(), Signal(), Signal()
        m.d.comb += [
            ctl0.eq(0),
            ctl1.eq(0),
            ctl2.eq(0),
            ctl3.eq(0),
        ]
        m.submodules.blueTmds, m.submodules.greenTmds, m.submodules.redTmds = (
            blueTmds,
            greenTmds,
            redTmds,
        ) = (
            DomainRenamer("pixel")(DviTmdsEncoder(blue, vde, hsync, vsync)),
            DomainRenamer("pixel")(DviTmdsEncoder(green, vde, ctl0, ctl1)),
            DomainRenamer("pixel")(DviTmdsEncoder(red, vde, ctl2, ctl3)),
        )

        channelClockSource = Signal(10)
        # m.d.comb += channelClockSource.eq(0b1111100000)
        m.d.comb += channelClockSource.eq(0b0000011111)
        (
            m.submodules.channel0,
            m.submodules.channel1,
            m.submodules.channel2,
            m.submodules.channelClock,
        ) = (channel0, channel1, channel2, channelClock) = (
            DomainRenamer("dviLink")(ShiftRegisterSendLsbFirst(blueTmds.ports()[-1])),
            DomainRenamer("dviLink")(ShiftRegisterSendLsbFirst(greenTmds.ports()[-1])),
            DomainRenamer("dviLink")(ShiftRegisterSendLsbFirst(redTmds.ports()[-1])),
            DomainRenamer("dviLink")(ShiftRegisterSendLsbFirst(channelClockSource)),
        )

        hdmiMain = platform.request("hdmi", 0)
        m.d.comb += [
            hdmiMain.c0_p.eq(channel0.dataOut),
            hdmiMain.c0_n.eq(channel0.dataOutInverted),
            hdmiMain.c1_p.eq(channel1.dataOut),
            hdmiMain.c1_n.eq(channel1.dataOutInverted),
            hdmiMain.c2_p.eq(channel2.dataOut),
            hdmiMain.c2_n.eq(channel2.dataOutInverted),
            hdmiMain.c3_p.eq(channelClock.dataOut),
            hdmiMain.c3_n.eq(channelClock.dataOutInverted),
        ]

        ### What you should get at this point
        #
        # * A blinking onboard led, 1Hz
        # * Through a display plugged into the HDMI port, a solid colored surface with a color alternating betwen a blue-ish #0055AA and yellow-ish #AA9955.
        #
        ###

        return m
