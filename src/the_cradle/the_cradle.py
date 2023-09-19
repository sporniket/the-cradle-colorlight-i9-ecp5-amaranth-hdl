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
from amaranth_stuff.modules import Sequencer

## pll parameters to get the frequencies [270, 108, 27, 31]MHz
mainPllParameters = {
    "p_PLLRST_ENA": "DISABLED",
    "p_INTFB_WAKE": "DISABLED",
    "p_STDBY_ENABLE": "DISABLED",
    "p_DPHASE_SOURCE": "DISABLED",
    "p_OUTDIVIDER_MUXA": "DIVA",
    "p_OUTDIVIDER_MUXB": "DIVB",
    "p_OUTDIVIDER_MUXC": "DIVC",
    "p_OUTDIVIDER_MUXD": "DIVD",
    "p_CLKI_DIV": 5,
    "p_CLKOP_ENABLE": "ENABLED",
    "p_CLKOP_DIV": 2,
    "p_CLKOP_CPHASE": 1,
    "p_CLKOP_FPHASE": 0,
    "p_CLKOS_ENABLE": "ENABLED",
    "p_CLKOS_DIV": 5,
    "p_CLKOS_CPHASE": 1,
    "p_CLKOS_FPHASE": 0,
    "p_CLKOS2_ENABLE": "ENABLED",
    "p_CLKOS2_DIV": 20,
    "p_CLKOS2_CPHASE": 1,
    "p_CLKOS2_FPHASE": 0,
    "p_CLKOS3_ENABLE": "ENABLED",
    "p_CLKOS3_DIV": 17,
    "p_CLKOS3_CPHASE": 1,
    "p_CLKOS3_FPHASE": 0,
    "p_FEEDBK_PATH": "CLKOP",
    "p_CLKFB_DIV": 54,
    "i_RST": 0,
    "i_STDBY": 0,
    "i_PHASESEL0": 0,
    "i_PHASESEL1": 0,
    "i_PHASEDIR": 1,
    "i_PHASESTEP": 1,
    "i_PHASELOADREG": 1,
    "i_PLLWAKESYNC": 0,
    "i_ENCLKOP": 0,
}

## Video timings for 720x576@50Hz
## sequence of pixels in a single scan line [sync, back porch, active, front porch]
pixelSequence = [64, 68, 720, 12]  # total = 864

## sequence of scanlines in a video screen [sync, back porch, active, front porch]
scanlineSequence = [5, 39, 576, 5]  # total = 625


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

        domTheCradle = ClockDomain(
            "theCradle", local=True
        )  # save for later, unused now
        m.d.comb += domTheCradle.clk.eq(mainPll.clkout1)

        domPixel = ClockDomain(
            "pixel", local=True
        )  # for the TMDS encoder and the pixel source.
        m.d.comb += domPixel.clk.eq(mainPll.clkout2, local=True)

        domCpuBase = ClockDomain(
            "cpuBase", local=True
        )  # base for clocking the external CPU, unused now
        m.d.comb += domCpuBase.clk.eq(mainPll.clkout3, local=True)

        ### Pixel sequencer -> hsync clock
        m.submodules.pixelSequencer = pixelSequencer = DomainRenamer("pixel")(
            Sequencer(pixelSequence)
        )
        hsync = pixelSequencer.steps[0]
        henable = pixelSequencer.steps[2]

        domHsync = ClockDomain("hsync", local=True)
        m.d.comb += domHsync.clk.eq(hsync)

        ### Scanline sequencer -> vsync clock + video display enable
        m.submodules.scanlineSequencer = scanlineSequencer = DomainRenamer("hsync")(
            Sequencer(scanlineSequence)
        )
        vsync = scanlineSequencer.steps[0]
        venable = scanlineSequencer.steps[2]

        vde = Signal()
        m.d.comb += vde.eq(venable & henable)

        hsyncActive = Signal()  # Hsync pulse only for lines with displayable area
        m.d.comb += hsyncActive.eq(venable & hsync)

        domVsync = ClockDomain("vsync", local=True)
        m.d.comb += domVsync.clk.eq(vsync)

        domHsyncActive = ClockDomain(
            "hsyncActive", local=True
        )  # in effect, serves to clock a counter of displayed line, reset at each vbl.
        m.d.comb += [domHsyncActive.clk.eq(hsyncActive), domHsyncActive.rst.eq(vsync)]

        ### The pixel source
        videoSource = videoSolidBlink = Signal(
            24
        )  # v[0:8] = blue, v[8:16] = green, v[16:24] = blue
        m.d.comb += videoSolidBlink.eq(
            Mux(blinky.submodules.beat.beat_p, 0x0055AA, 0xAA9955)
        )

        # TODO : step 1 : checkered, 16x8 pattern
        # TODO : step 2 : colorful gradient tiles
        ### The dvi link
        m.submodules.blueTmds, m.submodules.greenTmds, m.submodules.redTmds = (
            blueTmds,
            greenTmds,
            redTmds,
        ) = (
            DomainRenamer("pixel")(DviTmdsEncoder(videoSource[0:8], vde, hsync, vsync)),
            DomainRenamer("pixel")(DviTmdsEncoder(videoSource[8:16], vde, 0, 0)),
            DomainRenamer("pixel")(DviTmdsEncoder(videoSource[16:24], vde, 0, 0)),
        )

        (
            m.submodules.channel0,
            m.submodules.channel1,
            m.submodules.channel2,
            m.submodules.channelClock,
        ) = (channel0, channel1, channel2, channelClock) = (
            DomainRenamer("dviLink")(ShiftRegisterTx(blueTmds.ports[-1])),
            DomainRenamer("dviLink")(ShiftRegisterTx(greenTmds.ports[-1])),
            DomainRenamer("dviLink")(ShiftRegisterTx(redTmds.ports[-1])),
            DomainRenamer("dviLink")(
                ShiftRegisterTx(Signal(unsigned(10), reset=0b0000011111))
            ),
        )
        # TODO : the ressource gpios of the hdmi link, using the output of the shift registers

        ### What you should get at this point
        #
        # * A blinking onboard led, 1Hz
        # * Through a display plugged into the HDMI port, a pattern (either solid blue-ish, or a checkered pattern, or colored gradient tiles)
        #
        ###

        return m
