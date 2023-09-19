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
from .blinky import Blinky
from .ecp5 import PllInstance
from amaranth_stuff.modules import (
    Sequencer,
    SlowBeat,
    ShiftRegisterSendLsbFirst,
    DviTmdsEncoder,
)

from .vid_settings_640x480_59Hz94 import mainPllParameters, pixelSequence, scanlineSequence 
# from .vid_settings_720x576_50Hz import mainPllParameters, pixelSequence, scanlineSequence 


class TheCradle(Elaboratable):
    def __init__(self):
        pass

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        ## Setup blinky : shows that the fpga is running
        m.submodules.blinky = blinky = Blinky()

        ### Main pll and clocks
        m.submodules.mainPll = mainPll = PllInstance(mainPllParameters)

        domDviLink = ClockDomain(
            "dviLink", local=True
        )  # for the shift registers receiving TMDS encoded data
        m.d.comb += domDviLink.clk.eq(mainPll.clkout0)
        m.domains += domDviLink

        domTheCradle = ClockDomain(
            "theCradle", local=True
        )  # save for later, unused now
        m.d.comb += domTheCradle.clk.eq(mainPll.clkout1)
        m.domains += domTheCradle

        domPixel = ClockDomain(
            "pixel", local=True
        )  # for the TMDS encoder and the pixel source.
        m.d.comb += domPixel.clk.eq(mainPll.clkout2)
        m.domains += domPixel

        domCpuBase = ClockDomain(
            "cpuBase", local=True
        )  # base for clocking the external CPU, unused now
        m.d.comb += domCpuBase.clk.eq(mainPll.clkout3)
        m.domains += domCpuBase

        ### Pixel sequencer -> hsync clock
        m.submodules.pixelSequencer = pixelSequencer = DomainRenamer("sync")(
            Sequencer(pixelSequence)
        )
        hsync = Signal()
        m.d.comb += hsync.eq(pixelSequencer.steps[0])
        henable = pixelSequencer.steps[2]

        domHsync = ClockDomain("hsync", local=True)
        m.d.comb += domHsync.clk.eq(hsync)
        m.domains += domHsync

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

        domVsync = ClockDomain("vsync", local=True)
        m.d.comb += domVsync.clk.eq(vsync)
        m.domains += domVsync

        domHsyncActive = ClockDomain(
            "hsyncActive", local=True
        )  # in effect, serves to clock a counter of displayed line, reset at each vbl.
        m.d.comb += [domHsyncActive.clk.eq(hsyncActive), domHsyncActive.rst.eq(vsync)]
        m.domains += domHsyncActive

        ### The pixel source
        videoSource = videoSolidBlink = Signal(
            24
        )  # v[0:8] = blue, v[8:16] = green, v[16:24] = blue
        m.submodules.beat = beat = SlowBeat(1)
        m.d.comb += videoSolidBlink.eq(Mux(beat.beat_p, 0x0055AA, 0xAA9955))
        red, green, blue = Signal(8), Signal(8), Signal(8)
        m.d.comb += [
            blue.eq(videoSource[0:8]),
            green.eq(videoSource[8:16]),
            red.eq(videoSource[16:24]),
        ]

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
            DomainRenamer("sync")(DviTmdsEncoder(blue, vde, hsync, vsync)),
            DomainRenamer("sync")(DviTmdsEncoder(green, vde, ctl0, ctl1)),
            DomainRenamer("sync")(DviTmdsEncoder(red, vde, ctl2, ctl3)),
        )

        channelClockSource = Signal(10)
        m.d.comb += channelClockSource.eq(0b1111100000)
        # m.d.comb += channelClockSource.eq(0b0000011111)
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
        # * Through a display plugged into the HDMI port, a pattern (either solid blue-ish, or a checkered pattern, or colored gradient tiles)
        #
        ###

        return m
